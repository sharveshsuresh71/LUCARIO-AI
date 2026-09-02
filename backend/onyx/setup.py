import time

from sqlalchemy.orm import Session

from onyx.configs.app_configs import (
    DISABLE_INDEX_UPDATE_ON_SWAP,
    DISABLE_VECTOR_DB,
    ENABLE_OPENSEARCH_INDEXING_FOR_ONYX,
    INTEGRATION_TESTS_MODE,
    MANAGED_VESPA,
    ONYX_DISABLE_VESPA,
    VESPA_NUM_ATTEMPTS_ON_STARTUP,
)
from onyx.configs.constants import KV_REINDEX_KEY
from onyx.configs.embedding_configs import (
    SUPPORTED_EMBEDDING_MODELS,
    SupportedEmbeddingModel,
)
from onyx.configs.model_configs import GEN_AI_API_KEY, GEN_AI_MODEL_VERSION
from onyx.context.search.models import SavedSearchSettings
from onyx.db.connector import check_connectors_exist, create_initial_default_connector
from onyx.db.connector_credential_pair import (
    associate_default_cc_pair,
    get_connector_credential_pairs,
    resync_cc_pair,
)
from onyx.db.credentials import create_initial_public_credential
from onyx.db.document import check_docs_exist
from onyx.db.enums import EmbeddingPrecision
from onyx.db.index_attempt import (
    cancel_indexing_attempts_past_model,
    expire_index_attempts,
)
from onyx.db.llm import (
    fetch_default_llm_model,
    fetch_existing_llm_provider,
    update_default_provider,
    upsert_llm_provider,
)
from onyx.db.search_settings import (
    get_active_search_settings,
    get_current_search_settings,
    update_current_search_settings,
)
from onyx.db.swap_index import check_and_perform_index_swap
from onyx.document_index.factory import get_all_document_indices
from onyx.document_index.interfaces_new import DocumentIndex
from onyx.document_index.opensearch.client import (
    OpenSearchClient,
    OpenSearchIndexWriteBlockedError,
    wait_for_opensearch_with_timeout,
)
from onyx.document_index.opensearch.opensearch_document_index import set_cluster_state
from onyx.document_index.vespa.vespa_document_index import (
    register_multitenant_vespa_indices,
)
from onyx.indexing.models import IndexingSetting
from onyx.key_value_store.factory import get_kv_store
from onyx.key_value_store.interface import KvKeyNotFoundError
from onyx.llm.constants import LlmProviderNames
from onyx.natural_language_processing.search_nlp_models import (
    EmbeddingModel,
    warm_up_bi_encoder,
)
from onyx.server.manage.llm.models import (
    LLMProviderUpsertRequest,
    ModelConfigurationUpsertRequest,
)
from onyx.server.settings.store import (
    load_settings,
    settings_write_lock,
    store_settings,
)
from onyx.utils.gpu_utils import gpu_status_request
from onyx.utils.logger import setup_logger
from shared_configs.configs import (
    ALT_INDEX_SUFFIX,
    MODEL_SERVER_HOST,
    MODEL_SERVER_PORT,
    MULTI_TENANT,
)

logger = setup_logger()


def setup_onyx(
    db_session: Session,
    tenant_id: str,
    cohere_enabled: bool = False,
) -> None:
    """
    Setup Onyx for a particular tenant. In the Single Tenant case, it will set it up for the default schema
    on server startup. In the MT case, it will be called when the tenant is created.

    The Tenant Service calls the tenants/create endpoint which runs this.
    """
    check_and_perform_index_swap(db_session=db_session)

    active_search_settings = get_active_search_settings(db_session)
    search_settings = active_search_settings.primary
    secondary_search_settings = active_search_settings.secondary

    if secondary_search_settings and DISABLE_INDEX_UPDATE_ON_SWAP:
        expire_index_attempts(
            search_settings_id=search_settings.id, db_session=db_session
        )

        for cc_pair in get_connector_credential_pairs(db_session):
            resync_cc_pair(
                cc_pair=cc_pair,
                search_settings_id=search_settings.id,
                db_session=db_session,
            )

    cancel_indexing_attempts_past_model(db_session)

    logger.notice('Using Embedding model: "%s"', search_settings.model_name)
    if search_settings.query_prefix or search_settings.passage_prefix:
        logger.notice("Query embedding prefix: %s", search_settings.query_prefix)
        logger.notice("Passage embedding prefix: %s", search_settings.passage_prefix)

    setup_postgres(db_session)

    if not MULTI_TENANT:
        mark_reindex_flag(db_session)

    if DISABLE_VECTOR_DB:
        logger.notice(
            "DISABLE_VECTOR_DB is set — skipping document index setup and embedding model warm-up."
        )
    else:
        logger.notice("Verifying Document Index(s) is/are available.")

        document_indices = get_all_document_indices(
            search_settings,
            secondary_search_settings,
            None,
        )

        success = setup_document_indices(
            document_indices,
            IndexingSetting.from_db_model(search_settings),
        )

        if not success:
            raise RuntimeError(
                "Could not connect to a document index within the specified timeout."
            )

        logger.notice(
            "Model Server: http://%s:%s", MODEL_SERVER_HOST, MODEL_SERVER_PORT
        )

        if search_settings.provider_type is None:
            warm_up_bi_encoder(
                embedding_model=EmbeddingModel.from_db_model(
                    search_settings=search_settings,
                    server_host=MODEL_SERVER_HOST,
                    server_port=MODEL_SERVER_PORT,
                ),
                non_blocking=INTEGRATION_TESTS_MODE,
            )

        update_default_multipass_indexing(db_session)


def mark_reindex_flag(db_session: Session) -> None:
    kv_store = get_kv_store()

    try:
        value = kv_store.load(KV_REINDEX_KEY)
        logger.debug("Re-indexing flag has value %s", value)
        return
    except KvKeyNotFoundError:
        pass

    docs_exist = check_docs_exist(db_session)
    connectors_exist = check_connectors_exist(db_session)

    if docs_exist or connectors_exist:
        kv_store.store(KV_REINDEX_KEY, True)
    else:
        kv_store.store(KV_REINDEX_KEY, False)


def setup_document_indices(
    document_indices: list[DocumentIndex],
    index_setting: IndexingSetting,
    num_attempts: int = VESPA_NUM_ATTEMPTS_ON_STARTUP,
) -> bool:
    """Sets up all input document indices."""

    for document_index in document_indices:
        WAIT_SECONDS = 5
        document_index_setup_success = False

        for x in range(num_attempts):
            try:
                logger.notice(
                    "Setting up document index %s (attempt %s/%s)...",
                    document_index.__class__.__name__,
                    x + 1,
                    num_attempts,
                )

                document_index.verify_and_create_index_if_necessary(
                    embedding_dim=index_setting.final_embedding_dim,
                    embedding_precision=index_setting.embedding_precision,
                )

                logger.notice(
                    "Document index %s setup complete.",
                    document_index.__class__.__name__,
                )

                document_index_setup_success = True
                break

            except OpenSearchIndexWriteBlockedError as e:
                logger.error(
                    "Document index %s is write-blocked; continuing startup without "
                    "the mapping refresh. Search still works, but indexing will fail "
                    "until the block is cleared. Error: %s",
                    document_index.__class__.__name__,
                    e,
                )

                document_index_setup_success = True
                break

            except Exception:
                logger.exception(
                    "Document index %s setup did not succeed. "
                    "The relevant service may not be ready yet. "
                    "Retrying in %s seconds.",
                    document_index.__class__.__name__,
                    WAIT_SECONDS,
                )

                time.sleep(WAIT_SECONDS)

        if not document_index_setup_success:
            logger.error(
                "Document index %s setup did not succeed. "
                "Attempt limit reached. (%s)",
                document_index.__class__.__name__,
                num_attempts,
            )

            return False

    return True


def setup_postgres(db_session: Session) -> None:
    logger.notice("Verifying default connector/credential exist.")

    create_initial_public_credential(db_session)
    create_initial_default_connector(db_session)
    associate_default_cc_pair(db_session)

    if GEN_AI_API_KEY and fetch_default_llm_model(db_session) is None:
        # Google Gemini development setup
        logger.notice("Setting up default Google Gemini LLM for dev.")

        llm_model = GEN_AI_MODEL_VERSION or "gemini-3-flash-preview"
        provider_name = "DevEnvPresetGoogle"

        existing = fetch_existing_llm_provider(
            name=provider_name,
            db_session=db_session,
        )

        model_req = LLMProviderUpsertRequest(
            id=existing.id if existing else None,
            name=provider_name,
            provider=LlmProviderNames.GOOGLE,
            api_key=GEN_AI_API_KEY,
            api_base=None,
            api_version=None,
            custom_config=None,
            is_public=True,
            groups=[],
            model_configurations=[
                ModelConfigurationUpsertRequest(
                    name=name,
                    is_visible=True,
                )
                for name in get_google_model_names()
            ],
            api_key_changed=True,
        )

        try:
            new_llm_provider = upsert_llm_provider(
                llm_provider_upsert_request=model_req,
                db_session=db_session,
            )
        except ValueError as e:
            logger.warning(
                "Failed to upsert Google Gemini provider during setup: %s",
                e,
            )
            return

        update_default_provider(
            provider_id=new_llm_provider.id,
            model_name=llm_model,
            db_session=db_session,
        )


def update_default_multipass_indexing(db_session: Session) -> None:
    docs_exist = check_docs_exist(db_session)
    connectors_exist = check_connectors_exist(db_session)

    logger.debug(
        "Docs exist: %s, Connectors exist: %s",
        docs_exist,
        connectors_exist,
    )

    if not docs_exist and not connectors_exist:
        logger.info(
            "No existing docs or connectors found. "
            "Checking GPU availability for multipass indexing."
        )

        gpu_available = gpu_status_request(indexing=True)

        logger.info("GPU available: %s", gpu_available)

        current_settings = get_current_search_settings(db_session)

        logger.notice(
            "Updating multipass indexing setting to: %s",
            gpu_available,
        )

        updated_settings = SavedSearchSettings.from_db_model(current_settings)
        updated_settings.multipass_indexing = (
            gpu_available or current_settings.cloud_provider is not None
        )

        update_current_search_settings(
            db_session,
            updated_settings,
        )

        with settings_write_lock():
            settings = load_settings()
            settings.gpu_enabled = gpu_available
            store_settings(settings)

        logger.notice(
            "Updated settings with GPU availability: %s",
            gpu_available,
        )

    else:
        logger.debug(
            "Existing docs or connectors found. "
            "Skipping multipass indexing update."
        )


def setup_multitenant_onyx() -> None:
    if DISABLE_VECTOR_DB:
        logger.notice(
            "DISABLE_VECTOR_DB is set — skipping multitenant Vespa setup."
        )
        return

    if ENABLE_OPENSEARCH_INDEXING_FOR_ONYX:
        opensearch_client = OpenSearchClient()

        if not wait_for_opensearch_with_timeout(
            client=opensearch_client
        ):
            raise RuntimeError("Failed to connect to OpenSearch.")

        set_cluster_state(opensearch_client)

    if not MANAGED_VESPA and not ONYX_DISABLE_VESPA:
        setup_vespa_multitenant(SUPPORTED_EMBEDDING_MODELS)


def setup_vespa_multitenant(
    supported_indices: list[SupportedEmbeddingModel],
) -> bool:
    WAIT_SECONDS = 5
    VESPA_ATTEMPTS = 5

    for x in range(VESPA_ATTEMPTS):
        try:
            logger.notice(
                "Setting up Vespa (attempt %s/%s)...",
                x + 1,
                VESPA_ATTEMPTS,
            )

            register_multitenant_vespa_indices(
                indices=[
                    index.index_name for index in supported_indices
                ]
                + [
                    f"{index.index_name}{ALT_INDEX_SUFFIX}"
                    for index in supported_indices
                ],
                embedding_dims=[
                    index.dim for index in supported_indices
                ]
                + [
                    index.dim for index in supported_indices
                ],
                embedding_precisions=[
                    EmbeddingPrecision.FLOAT
                    for _ in range(len(supported_indices) * 2)
                ],
            )

            logger.notice("Vespa setup complete.")
            return True

        except Exception:
            logger.notice(
                "Vespa setup did not succeed. "
                "The Vespa service may not be ready yet. "
                "Retrying in %s seconds.",
                WAIT_SECONDS,
            )

            time.sleep(WAIT_SECONDS)

    logger.error(
        "Vespa setup did not succeed. Attempt limit reached. (%s)",
        VESPA_ATTEMPTS,
    )

    return False

