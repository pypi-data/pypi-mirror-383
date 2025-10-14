# INVALID_TOC_STR_1 ='{"tocSequenceNum":"32","documentFileLen":"102278","tocStyle":"outlinetxt2","tocLevel":"3","tocName":"18. "Suit" means a civil proceeding in which damages because of "loss of elect""}'
# INVALID_TOC_STR_2 = '{"tocSequenceNum":"3","documentFileLen":"68837","tocStyle":"outlinetxt2","tocLevel":"3","tocName":"1.   "Bodily injury" or "property damage" caused by a "cyber incident"; and"}'
# TRANSFORMED_TOC_1 = '{"tocSequenceNum":"32","documentFileLen":"102278","tocStyle":"outlinetxt2","tocLevel":"3","tocName":"18.   \\"Suit\\" means a civil proceeding in which damages because of \\"loss of elect\\""}'
# TRANSFORMED_TOC_2 = '{"tocSequenceNum":"3","documentFileLen":"68837","tocStyle":"outlinetxt2","tocLevel":"3","tocName":"1.   \\"Bodily injury\\" or \\"property damage\\" caused by a \\"cyber incident\\"; and"}'
# DEFAULT_LOB = "BP"
# MU_STATE_CODES_LIST = ["MU", "00"]

REGIONS = ["us-east-1","us-west-2","eu-west-1","eu-west-2","eu-west-3","sa-east-1","ap-south-1","ap-southeast-2","ca-central-1","eu-central-1",""]  # Add more as needed
MAX_RETRIES= 3
SERVICE_CODE= "bedrock"
OPEN_SEARCH_DOC_SIZE = 200


REGULAR_INDEX_FLAG = "regular"
TOC_INDEX_FLAG = "toc"
GLOBAL_SEARCH_FLAG_EI = "ei_data"

MAX_RETRIES_NUM = 20
BACKOFF_FACTOR_NUM = 2
LLM_TOKEN_LIMIT = 100000
EMBEDDING_MODEL_TOKEN_LIMIT = 7000
MU_FILE_NAME = "mu-final.json"

STATUS_PROCESSED = "Processed"
STATUS_FAILED = "Failed"
GSI2_PARTITIONKEY_PREFIX = "STATUS#"
PARTITIONKEY_VALUE = "DOC#"
TRANSACTIONID_PREFIX = "TS#"
DEFAULT_REGION = "us-east-1"
DEFAULT_SQS_BATCH_SIZE = 10
DEFAULT_SQS_WAIT_TIME = 20
DEFAULT_SQS_RETRIES = 5
MAX_SQS_POLL_RETRIES = 3
PRODUCT_NAME = "GlobalInsights"
DATATYPE = "DataLoad"
INVALID_SQS_MESSAGE = "Invalid SQS Message"


addiitonal_rule_mapping = {
    "CT": "Class Table",
    "FO": "Forms/Endorsements",
    "RU": "Rules -- State Exception and Multistate",
    "RUA": "Additional Rules",
    "ELP": "Estimated Loss Potentials",
    "ILTA": "Increased Limits Table Assignments",
    "ILADD": "Increased Limits Table Assignments Addendum",
    "LCADD": "Loss Cost Addendum",
    "CWRLC": "Loss Costs/Rates",
    "CWR": "Multistate Loss Costs/Rates",
    "NTM": "Notice To Manualholders",
    "APT": "NY Apartment Transition Factors",
    "R": "State Loss Costs/Rates",
    "T": "Territory",
    "TF": "Transition Factors"
}
