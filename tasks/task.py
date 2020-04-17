
import json
from tasks.cp import CpTaskBase
from models.cp import Cp
from loguru import logger

def add_task(scheduler=None):

    for item in Cp.select():

        cpTask = CpTaskBase(id=item.id)

        logger.info("{}任务表加载中...".format(item.name))


        tables = json.loads(item.tasktimetable)['tables']

        tables.sort(key=lambda k: (k.get('id')), reverse=False)

        for index,taskItem in enumerate(tables):

            next_autoid = tables[0]['id']  if index+1>=len(tables) else tables[index + 1]['id']

            if taskItem['opentime'] == '0000':
                scheduler.add_job(cpTask.getCp, 'cron',
                                  hour=23,
                                  minute=59,
                                  second=59,
                                  kwargs={
                                      "autoid":taskItem['id'],
                                      "next_autoid":next_autoid
                                  })
            else:
                scheduler.add_job(cpTask.getCp, 'cron',
                                  hour=int(taskItem['opentime'][:2]),
                                  minute=int(taskItem['opentime'][2:]),
                                  kwargs={
                                      "autoid":taskItem['id'],
                                      "next_autoid":next_autoid
                                  })

if __name__ == '__main__':
    import sys,os
    from models.cp import Cp
    PROJECT_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.path.pardir)
    if PROJECT_PATH not in sys.path:
        sys.path.insert(0, PROJECT_PATH)

    # import json
    #
    # from tasks.cp import CpTaskBase
    # from models.cp import Cp
    # from loguru import logger

    add_task()