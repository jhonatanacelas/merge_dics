import unittest

from ..merge_dics import merge_events


class TestMergeEvents(unittest.TestCase):

    def setUp(self):
        self.event1 = {
            "event_type": "FLT_TAKEOFF",
            "event_timestamp": "2024-02-26T12:30:00.000Z",
            "customer_id": "0008007683728",
            "flight_segments": [
                {
                    "trip_number": "1",
                    "marketed_carrier": "DL",
                    "origin_airport": "BHM",
                    "destination_airport": "ATL",
                    "scheduled_departure_time": "12:30:00",
                    "actual_departure_time": "12:30:00",
                    "seats": [{"seat_number": "30C", "seat_status": "HK"}],
                }
            ],
        }
        self.event2 = {
            "event_type": "FLT_TAKEOFF",
            "record_locator_create_date": "2023-06-27",
            "flight_segments": [
                {
                    "trip_number": "1",
                    "scheduled_flight_length": "00:05:00",
                    "origin_airport": "ATL",
                    "actual_departure_time": "21:05:00",
                    "seats": [
                        {
                            "seat_number": "30C",
                            "seat_status": "HK",
                        },
                        {"seat_number": "15A", "seat_status": "CI"},
                    ],
                }
            ],
        }

    def test_with_new_attributes(self):
        self.assertEqual(
            merge_events(
                db_event={"attr1": "x", "attr2": "y"},
                new_event={"attr1": "x", "attr2": "y", "attr3": "z"},
            ),
            {"attr1": "x", "attr2": "y", "attr3": "z"},
        )

    def test_with_different_values(self):
        self.assertEqual(
            merge_events(
                db_event={"attr1": "x", "attr2": "y"},
                new_event={"attr1": "k", "attr2": "j"},
            ),
            {"attr1": "k", "attr2": "j"},
        )

    def test_with_new_attributes_and_different_common_data(self):
        self.assertEqual(
            merge_events(
                db_event={"attr1": "x", "attr2": "y"},
                new_event={"attr2": "j", "attr3": "z"},
            ),
            {"attr1": "x", "attr2": "j", "attr3": "z"},
        )

    def test_with_new_attributes_and_same_common_data(self):
        self.assertEqual(
            merge_events(
                db_event={"attr1": "x", "attr2": "y"},
                new_event={"attr2": "y", "attr3": "z"},
            ),
            {"attr1": "x", "attr2": "y", "attr3": "z"},
        )

    def test_event_does_not_exist(self):
        self.assertEqual(
            merge_events(
                db_event={}, new_event={"attr1": "k", "attr2": "j", "attr3": "z"}
            ),
            {"attr1": "k", "attr2": "j", "attr3": "z"},
        )

    def test_with_sub_array_no_dict_without_config_is_replaced(self):
        merged_result = merge_events(
            db_event={"attr1": "x", "attr2": "y", "attr3": ["a", "b"]},
            new_event={"attr2": "j", "attr3": ["c", "d"]},
        )

        self.assertEqual(merged_result["attr1"], "x")
        self.assertEqual(merged_result["attr2"], "j")
        # assertCountEqual in Python's unittest framework checks if two iterables (like lists) have the same elements in any order
        self.assertCountEqual(merged_result["attr3"], ["c", "d"])

    def test_basic_information_update(self):
        merged_event = merge_events(self.event1.copy(), self.event2)
        self.assertEqual(merged_event["record_locator_create_date"], "2023-06-27")
        self.assertEqual(merged_event["customer_id"], "0008007683728")

    def test_flight_segment_update(self):
        merged_event = merge_events(self.event1.copy(), self.event2)
        self.assertEqual(merged_event["flight_segments"][0]["origin_airport"], "ATL")
        # scheduled_departure_time
        self.assertEqual(
            merged_event["flight_segments"][0]["scheduled_departure_time"], "12:30:00"
        )
        self.assertEqual(
            merged_event["flight_segments"][0]["actual_departure_time"], "21:05:00"
        )

    def test_update_sub_array_elements(self):
        merged_event = merge_events(self.event1.copy(), self.event2)
        self.assertIn(
            {"seat_number": "15A", "seat_status": "CI"},
            merged_event["flight_segments"][0]["seats"],
        )
        self.assertIn(
            {"seat_number": "30C", "seat_status": "HK"},
            merged_event["flight_segments"][0]["seats"],
        )
