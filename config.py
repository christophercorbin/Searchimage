import logging

class BaseConfig():
    LOGGER_NAME = 'dme-searcher'
    LOGGER_LEVEL = logging.DEBUG
    LOGGER_NAME_EVENT_HANDLER_DME_SEARCHER = f'{LOGGER_NAME}.event_handler'
    LOGGER_NAME_EVENT_CONSUMER = f'{LOGGER_NAME}.event_consumer'
    LOGGER_NAME_EVENT_PRODUCER = f'{LOGGER_NAME}.event_producer'
    LOGGER_NAME_UTIL_SERVICE = f'{LOGGER_NAME}.util_service'
    LOGGER_NAME_IMAGE_SEARCH_REPO = f'{LOGGER_NAME}.image_search_repo'
    LOGGER_NAME_IMAGE_STORAGE_REPO = f'{LOGGER_NAME}.image_storage_repo'
    LOGGER_NAME_USER_IMAGE_REPO = f'{LOGGER_NAME}.user_image_repo'
    LOGGER_NAME_IMAGE_PROCESSOR = f'{LOGGER_NAME}.image_processor'
    LOGGER_NAME_SCAN_SERVICE = f'{LOGGER_NAME}.scan_service'
    LOGGER_NAME_SCAN_REPO = f'{LOGGER_NAME}.scan_repo'
    LOGGER_NAME_LEAK_REPO = f'{LOGGER_NAME}.leak_repo'
    LOGGER_NAME_FACE_IMAGE_SCORE_REPO = f'{LOGGER_NAME}.face_image_score_repo'
    LOGGER_NAME_WEB_IMAGE_REPO = f'{LOGGER_NAME}.web_image_repo'
    LOGGER_NAME_WEB_SEARCHER = f'{LOGGER_NAME}.web_searcher'
    LOGGER_NAME_SCRAPER = f'{LOGGER_NAME}.scraper'
    LOGGER_NAME_VECTOR_SEARCHER = f'{LOGGER_NAME}.vector_searcher'
    LOGGER_NAME_USER_SERVICE = f'{LOGGER_NAME}.user_service'
    LOGGER_NAME_SEARCH_STAT_REPO = f'{LOGGER_NAME}.search_stat_repo'

    EVENT_CONSUMER_SERVERS = 'b-1.protexxadev.78kot0.c12.kafka.us-east-1.amazonaws.com:9092,b-2.protexxadev.78kot0.c12.kafka.us-east-1.amazonaws.com:9092'
    EVENT_CONSUMER_GROUP_DME_SEARCHER_QUICK_ID = 'dme-searcher_group'
    EVENT_CONSUMER_GROUP_DME_SEARCHER_FULL_ID = 'dme-searcher-full_group'
    EVENT_TOPIC_DME_SEARCHER_QUICK = 'dme-searcher-dev'
    EVENT_TOPIC_DME_DETECTOR_QUICK = 'dme-detector-dev'
    EVENT_TOPIC_DME_SEARCHER_FULL = 'dme-searcher-full-dev'
    EVENT_TOPIC_DME_DETECTOR_FULL = 'dme-detector-full-dev'
    EVENT_CONSUMER_ENABLE_AUTO_OFFSET_STORE = False # https://protexxa.atlassian.net/browse/DEF-562?focusedCommentId=10953
    EVENT_CONSUMER_MAX_POLL_INTERVAL_MS = 3600000  # one hour, since the consumer takes a long time (in the ballpark of minutes to hours, especially full search on famous people)

    IMAGE_INFERENCE_ENDPOINT = 'defenderImageAnalyzerEndpointC5i'
    IMAGE_INFERENCE_ENDPOINT_QUICK = 'defenderImageAnalyzerEndpointC6i2x'

    # TODO: this must go into secrets manager
    DB_URL_SECRET = 'stage/mongodb'
    DB_NAME = 'dme-dev'
    SCAN_REPO_NAME = 'scans'
    USER_IMAGE_REPO_NAME = 'userImages'
    WEB_IMAGE_REPO_NAME = 'webImages'
    FACE_IMAGE_SCORE_REPO_NAME = 'faceImageScores'
    WEBSITE_REPO_NAME = 'websites'
    LEAK_REPO_NAME = 'leaks'
    SEARCH_STATS_REPO_NAME = 'searchStats'
    IMAGE_SEARCH_REPO_REGION = 'us-east-1'
    IMAGE_SEARCH_REPO_HOST = 'z04opduo9ov5uvfz398a.us-east-1.aoss.amazonaws.com'
    IMAGE_SEARCH_SERVICE_NAME = 'aoss' # for opensearch service 

    USER_PROFILE_SOURCE_STORAGE_BUCKET_NAME = 'api-protexxa-dev-4242' # from client (protexxa)
    WEB_IMAGE_STORAGE_BUCKET_NAME = 'dme-web-image-4242'
    USER_IMAGE_STORAGE_BUCKET_NAME = 'dme-user-image-4242'

    IMAGE_DOWNLOADER_API_KEY = 'b3bcca8f8d5330baacca47519a50158c777eaac2'

    DUPLICATE_PREVENTION = False
    MIN_SIMILARITY_SCORE_VECTOR_DB = 0.0027
    MIN_COSINE_SIMILARITY_VECTOR_DB = 0.81
    MAX_SIMILARITY_DISTANCE_VECTOR_DB = 0.19
    MAX_SIMILARITY_DISTANCE_DEEPFACE = 0.35
    MAX_MACTHING_SIMILARITY_DISTANCE = 0.07 # Max matching similarity distance (TAG-1229)
    MAX_GPU_MEMORY = 1024 # 1GB
    MAX_NUM_FACE_VECTORS_TO_SEARCH = 60
    MAX_PAGES_TO_SEARCH_QUICK = 1 # Max pages to search in quick flow
    MAX_SEARCH_RESULTS_PER_PAGE_QUICK = 10 # Max search results in quick flow
    MAX_PAGES_TO_SEARCH_FULL = 1 # Max pages to search in full flow
    MAX_SEARCH_RESULTS_PER_PAGE_FULL = 20 # Max search results in full flow

    PURGE_SCRAPPED_DATA = True

    # Set of companies that are not real companies (for demo / poc purposes) and should be filtered out
    COMPANY_NAME_FILTER = {"DemoCo - Get your score.", "TestFilteredCompany co"}
    # Set of common email providers
    COMMON_EMAIL_PROVIDERS = {
        'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icloud.com',
        'live.com', 'aol.com', 'protonmail.com', 'zoho.com', 'mail.com',
        'gmx.com', 'yandex.com', 'tutanota.com', 'rediffmail.com', 'inbox.com',
        'hushmail.com', 'comcast.net', 'verizon.net', 'charter.net', 'cox.net',
        'earthlink.net', 'bellsouth.net', 'sbcglobal.net', 'att.net', 'roadrunner.com',
        'optonline.net', 'sky.com', 'btinternet.com', 'virginmedia.com', 'ntlworld.com',
        'telus.net', 'me.com', 'msn.com', 'skynet.be', 'qq.com', 'naver.com', 'hanmail.net'
    }

class TestConfig(BaseConfig):
    DB_URL = 'mongodb://localhost:27017/'
    DB_URL_SECRET = 'test/mongodb'
    DB_NAME = 'dme-test'
    EVENT_CONSUMER_GROUP_DME_SEARCHER_QUICK_ID = 'dme-searcher-test-group' # to avoid conflict with dev consumer group since they share the same broker
    EVENT_CONSUMER_GROUP_DME_SEARCHER_FULL_ID = 'dme-searcher-full-test-group'  # to avoid conflict with dev consumer group since they share the same broker
    EVENT_TOPIC_DME_SEARCHER_QUICK = 'dme-searcher-test'
    EVENT_TOPIC_DME_DETECTOR_QUICK = 'dme-detector-test'
    EVENT_TOPIC_DME_SEARCHER_FULL = 'dme-searcher-full-test'
    EVENT_TOPIC_DME_DETECTOR_FULL = 'dme-detector-full-test'
    IMAGE_INFERENCE_ENDPOINT = 'defenderImageAnalyzerEndpointC5i-test'
    IMAGE_INFERENCE_ENDPOINT_QUICK = 'defenderImageAnalyzerEndpointC6i2x-test'

    # Mimic the production environment for stress testing
    MAX_PAGES_TO_SEARCH_QUICK = 5
    MAX_SEARCH_RESULTS_PER_PAGE_QUICK = 100
    MAX_PAGES_TO_SEARCH_FULL = 5 # Set an upper limit for now so a user scan doesn't go on forever (ex: 10 pages * 100 results per page = 1000 results maximum per search term)
    MAX_SEARCH_RESULTS_PER_PAGE_FULL = 100 # 10 results: 1 credit, 20-100 results: 2 credits, we will use 100 results per page

class StageConfig(BaseConfig):
    LOGGER_FILE_DIR = '/home/ec2-user/logs'
    LOGGER_FILENAME_QUICK = 'log-quick-stage'
    LOGGER_FILENAME_FULL = 'log-full-stage'
    LOGGER_FILENAME_ANALYSIS = 'log-analysis-stage'
    EVENT_CONSUMER_SERVERS = 'b-2.protexxastg.umtlpe.c21.kafka.us-east-1.amazonaws.com:9092,b-1.protexxastg.umtlpe.c21.kafka.us-east-1.amazonaws.com:9092'
    EVENT_TOPIC_SCAN = 'protexxa-score-api-calls-stg-v2'
    EVENT_TOPIC_DME_SEARCHER_QUICK = 'dme-searcher-stg'
    EVENT_TOPIC_DME_DETECTOR_QUICK = 'dme-detector-stg'
    EVENT_TOPIC_DME_SEARCHER_FULL = 'dme-searcher-full-stg'
    EVENT_TOPIC_DME_DETECTOR_FULL = 'dme-detector-full-stg'
    EVENT_TOPIC_FULL = 'defender-image-full-search-stg'
    EVENT_TOPIC_ANALYSIS = 'defender-image-analysis-stg'
    EVENT_TOPIC_CONTENT = 'defender-user-content-search-stg'
    EVENT_TOPIC_IMAGE_REVERSE_EVENTS = 'new-found-stg'
    MAX_GPU_MEMORY = 1024
    MAX_NUM_FACE_VECTORS_TO_SEARCH = 60
    USER_PROFILE_SOURCE_STORAGE_BUCKET_NAME = 'api-protexxa-stg'
    DB_NAME = 'dme'
    IMAGE_SEARCH_REPO_HOST = 'vpc-protexxa-oss-image-k2yvnzlcojmcajroxvcfyqs6xy.us-east-1.es.amazonaws.com'
    IMAGE_SEARCH_SERVICE_NAME = 'es' # for opensearch service 
    WEB_IMAGE_STORAGE_BUCKET_NAME = 'dme-web-image'
    USER_IMAGE_STORAGE_BUCKET_NAME = 'dme-user-image'
    MAX_PAGES_TO_SEARCH_QUICK = 5
    MAX_SEARCH_RESULTS_PER_PAGE_QUICK = 100
    MAX_PAGES_TO_SEARCH_FULL = 5 # Set an upper limit for now so a user scan doesn't go on forever (ex: 10 pages * 100 results per page = 1000 results maximum per search term)
    MAX_SEARCH_RESULTS_PER_PAGE_FULL = 100 # 10 results: 1 credit, 20-100 results: 2 credits, we will use 100 results per page

class ProdConfig(BaseConfig):
    LOGGER_LEVEL = logging.INFO
    LOGGER_FILE_DIR = '/home/ec2-user/logs'
    LOGGER_FILENAME_QUICK = 'log-quick-prod'
    LOGGER_FILENAME_FULL = 'log-full-prod'
    LOGGER_FILENAME_ANALYSIS = 'log-analysis-prod'
    LOGGER_FILE_MAX_KB = 10240 # 10 MB
    LOGGER_FILE_MAX_NUM = 5
    EVENT_CONSUMER_SERVERS = 'b-2.protexxaprd.w4u9fe.c21.kafka.us-east-1.amazonaws.com:9092,b-1.protexxaprd.w4u9fe.c21.kafka.us-east-1.amazonaws.com:9092'
    EVENT_TOPIC_SCAN = 'protexxa-score-api-calls-prd'
    EVENT_TOPIC_DME_SEARCHER_QUICK = 'dme-searcher-prd'
    EVENT_TOPIC_DME_DETECTOR_QUICK = 'dme-detector-prd'
    EVENT_TOPIC_DME_SEARCHER_FULL = 'dme-searcher-full-prd'
    EVENT_TOPIC_DME_DETECTOR_FULL = 'dme-detector-full-prd'
    EVENT_TOPIC_FULL = 'defender-image-full-search-prd'
    EVENT_TOPIC_ANALYSIS = 'defender-image-analysis-prd'
    EVENT_TOPIC_CONTENT = 'defender-user-content-search-prd'
    EVENT_TOPIC_IMAGE_REVERSE_EVENTS = 'new-found-prd'
    MAX_GPU_MEMORY = 5120
    MAX_NUM_FACE_VECTORS_TO_SEARCH = 60
    USER_PROFILE_SOURCE_STORAGE_BUCKET_NAME = 'api-protexxa-prd'
    DB_URL_SECRET = 'production/mongodb'
    DB_NAME = 'dme'
    MAX_PAGES_TO_SEARCH_QUICK = 1
    MAX_SEARCH_RESULTS_PER_PAGE_QUICK = 100
    MAX_PAGES_TO_SEARCH_FULL = 5 # Set an upper limit for now so a user scan doesn't go on forever (ex: 10 pages * 100 results per page = 1000 results maximum per search term)
    MAX_SEARCH_RESULTS_PER_PAGE_FULL = 100 # 10 results: 1 credit, 20-100 results: 2 credits, we will use 100 results per page

class Prod1445Config(BaseConfig):
    LOGGER_LEVEL = logging.INFO
    EVENT_CONSUMER_SERVERS = 'b-3.defenderprod.n0znzr.c12.kafka.us-east-1.amazonaws.com:9092,b-2.defenderprod.n0znzr.c12.kafka.us-east-1.amazonaws.com:9092,b-1.defenderprod.n0znzr.c12.kafka.us-east-1.amazonaws.com:9092'
    EVENT_TOPIC_DME_SEARCHER_QUICK = 'dme-searcher-prd'
    EVENT_TOPIC_DME_DETECTOR_QUICK = 'dme-detector-prd'
    EVENT_TOPIC_DME_SEARCHER_FULL = 'dme-searcher-full-prd'
    EVENT_TOPIC_DME_DETECTOR_FULL = 'dme-detector-full-prd'
    MAX_NUM_FACE_VECTORS_TO_SEARCH = 60
    USER_PROFILE_SOURCE_STORAGE_BUCKET_NAME = 'api-protexxa-prod'
    DB_URL_SECRET = 'production/mongodb'
    DB_NAME = 'dme'
    IMAGE_SEARCH_REPO_HOST = '80brjbxl0042l7z3ab3.us-east-1.aoss.amazonaws.com'
    IMAGE_SEARCH_SERVICE_NAME = 'aoss' # for opensearch service 
    WEB_IMAGE_STORAGE_BUCKET_NAME = 'dme-web-images'
    USER_IMAGE_STORAGE_BUCKET_NAME = 'dme-user-images'
    MAX_PAGES_TO_SEARCH_QUICK = 5
    MAX_SEARCH_RESULTS_PER_PAGE_QUICK = 100
    MAX_PAGES_TO_SEARCH_FULL = 5 # Set an upper limit for now so a user scan doesn't go on forever (ex: 10 pages * 100 results per page = 1000 results maximum per search term)
    MAX_SEARCH_RESULTS_PER_PAGE_FULL = 100 # 10 results: 1 credit, 20-100 results: 2 credits, we will use 100 results per page



class Config():
    __instance = None
    __env = None

    @staticmethod
    def initialize(env):
        if Config.__instance is not None:
            return Config.__instance

        if env == 'prod':
            Config.__instance = ProdConfig()
        elif env == 'prod-1445':
            Config.__instance = Prod1445Config()
        elif env == 'test':
            Config.__instance = TestConfig()
        elif env == 'stage':
            Config.__instance = StageConfig()
        else:
            Config.__instance = BaseConfig()

        Config.__env = env
        return Config.__instance

    @staticmethod
    def get(env='dev'):
        if Config.__instance is None:
                Config.initialize(env)

        print(f'Applying configs for env: {Config.__env}')
        return Config.__instance