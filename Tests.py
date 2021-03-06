import unittest
from datetime import datetime, timedelta
from difflib import SequenceMatcher as SM
from peewee import *
from psutil import cpu_percent, virtual_memory
import config
import tracker
from app import views
from playhouse.shortcuts import model_to_dict


class Testui(unittest.TestCase):
    def setUp(self):
        config.DB = SqliteDatabase("test_track.db")
        config.QUERY_TIME = 30
        config.DB.create_tables([tracker.Entry], safe=True)
        # config.DB.create_tables(tracker.Entry,safe=True)
    # def tearDown(self):
    #     for i in tracker.Entry.select():
    #         i.delete_instance()

    def testClean_db(self):
        now = datetime.utcnow()
        tracker.Entry(time=now - timedelta(hours=11), name="old_entry_1", value=1).save()
        tracker.Entry(time=now - timedelta(hours=3), name="allowed_entry", value=1).save()
        tracker.clean_db()
        # assert tracker.Entry.select().where(tracker.Entry.name == "allowed_entry") is True
        # assert tracker.Entry.select().where(tracker.Entry.name == "old_entry_1") is False
        self.assertFalse(tracker.Entry.select().where(tracker.Entry.name == "old_entry_1"), msg="Entry not there")
        self.assertTrue(tracker.Entry.select().where(tracker.Entry.name == "allowed_entry"), msg="Entry there")

    def testmain(self):
        tracker.main()
        tracker.main()
        q = tracker.Entry.select().order_by(tracker.Entry.id.desc()).where(tracker.Entry.name == "RAM").get()
        # self.assertAlmostEqual(q.value,cpu_percent(interval=1))
        # self.assert(SM(None,q.value,cpu_percent(interval=1)).ratio() > 0.1)
        self.assertGreaterEqual(SM(None, str(q.value), str(virtual_memory()[2])).ratio(), 0.1,msg="Main has passed")

    def testApi(self):  # passes on travis
        now = datetime.utcnow()
        data1 = tracker.Entry(time=now, name="CPU0", value=2.5).save()
        data2 = tracker.Entry(time=now, name="CPU0", value=3).save()
        test_data = []
        # test_data = model_to_dict(data1)+","+model_to_dict(data2)
        for i in tracker.Entry.select().where(tracker.Entry.name == "CPU0"):
            test_data.append(model_to_dict(i))
        value = views.any_api("CPU0")
        self.assertTrue(str(test_data).strip("[]") == value, msg="API passed")


if __name__ == '__main__':
    unittest.main()

