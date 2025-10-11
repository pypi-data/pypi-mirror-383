from gitlab_ps_utils.logger import myLogger
from os import getcwd
from gitlab_ps_utils.api import GitLabApi
from gitlab_evaluate.lib.log_utils import get_log_level

glapi = GitLabApi(app_path=getcwd(), log_name='evaluate', timeout=120)
log_level = get_log_level()
glapi.log.setLevel(log_level)
if log_level == 'DEBUG':
    # Add httpx to the logs
    httpx_logger = myLogger('httpx')
    httpx_logger.setLevel(log_level)