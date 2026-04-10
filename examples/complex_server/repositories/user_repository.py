import time
from ..data.seed_data import USERS
from ..core.decorators import traceable
from ..core.logging_util import log_event

@traceable("user_repository.get_user_by_id")
def get_user_by_id(user_id: int):
    log_event(f"Fetching user {user_id} from repository")
    time.sleep(0.03)
    return USERS.get(user_id)