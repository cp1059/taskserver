
import json
from tasks.cp import CpTaskBase
from models.cp import Cp
from loguru import logger

def add_task(scheduler=None):

    for item in Cp.select():

        cpTask = CpTaskBase(id=item.id)

        logger.info("{}任务表加载中...".format(item.name))

        for item in json.loads(item.tasktimetable)['tables']:
            scheduler.add_job(cpTask.getCp, 'cron', hour=int(item[:2]),minute=int(item[2:]))

if __name__ == '__main__':
    import sys,os
    from models.cp import Cp
    PROJECT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir)
    if PROJECT_PATH not in sys.path:
        sys.path.insert(0, PROJECT_PATH)

    add_task()