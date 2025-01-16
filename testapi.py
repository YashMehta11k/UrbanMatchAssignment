import requests
import unittest
import json

class TestMarriageMatchmakingAPI(unittest.TestCase):
    BASE_URL = "http://localhost:8000"
    test_users = [
        {
            "name": "John Smith",
            "age": 30,
            "gender": "male",
            "email": "john.smith@test.com",
            "city": "New York",
            "interests": ["reading", "travel", "music"]
        },
        {
            "name": "Sarah Johnson",
            "age": 28,
            "gender": "female",
            "email": "sarah.j@test.com",
            "city": "New York",
            "interests": ["travel", "music", "cooking"]
        },
        {
            "name": "Emily Brown",
            "age": 31,
            "gender": "female",
            "email": "emily.b@test.com",
            "city": "Boston",
            "interests": ["sports", "reading"]
        }
    ]
    created_users = []

    def setUp(self):
        print("\nSetting up test users...")
        for user in self.test_users:
            response = requests.post(f"{self.BASE_URL}/users/", json=user)
            if response.status_code == 200:
                self.created_users.append(response.json())
                print(f"Created user: {user['name']}")

    def tearDown(self):
        print("\nCleaning up test users...")
        for user in self.created_users:
            response = requests.delete(f"{self.BASE_URL}/users/{user['id']}")
            if response.status_code == 204:
                print(f"Deleted user: {user['name']}")

    def test_1_email_validation(self):
        print("\nTesting email validation...")
        invalid_user = {
            "name": "Invalid Email User",
            "age": 25,
            "gender": "male",
            "email": "not-an-email",
            "city": "Chicago",
            "interests": ["testing"]
        }
        response = requests.post(f"{self.BASE_URL}/users/", json=invalid_user)
        self.assertEqual(response.status_code, 422)
        print("Email validation test passed")

    def test_2_user_update(self):
        print("\nTesting user update...")
        if not self.created_users:
            self.skipTest("No users available for update testing")
        
        user_id = self.created_users[0]['id']
        update_data = {
            "name": "John Smith Updated",
            "age": 31,
            "interests": ["reading", "travel", "music", "hiking"]
        }
        
        response = requests.put(f"{self.BASE_URL}/users/{user_id}", json=update_data)
        self.assertEqual(response.status_code, 200)
        updated_user = response.json()
        self.assertEqual(updated_user['name'], update_data['name'])
        self.assertEqual(updated_user['age'], update_data['age'])
        print("User update test passed")

    def test_3_user_deletion(self):
        print("\nTesting user deletion...")
        temp_user = {
            "name": "Temp User",
            "age": 25,
            "gender": "male",
            "email": "temp.user@test.com",
            "city": "Chicago",
            "interests": ["testing"]
        }
        create_response = requests.post(f"{self.BASE_URL}/users/", json=temp_user)
        self.assertEqual(create_response.status_code, 200)
        user_id = create_response.json()['id']
        
        delete_response = requests.delete(f"{self.BASE_URL}/users/{user_id}")
        self.assertEqual(delete_response.status_code, 204)
        
        get_response = requests.get(f"{self.BASE_URL}/users/{user_id}")
        self.assertEqual(get_response.status_code, 404)
        print("User deletion test passed")

    def test_4_matching_functionality(self):
        print("\nTesting matching functionality...")
        if len(self.created_users) < 2:
            self.skipTest("Not enough users for matching testing")
        
        male_user = next(user for user in self.created_users if user['gender'] == 'male')
        response = requests.get(f"{self.BASE_URL}/users/{male_user['id']}/matches")
        self.assertEqual(response.status_code, 200)
        
        matches = response.json()
        self.assertTrue(len(matches) > 0)
        
        for match in matches:
            self.assertNotEqual(match['gender'], male_user['gender'])
            self.assertTrue('compatibility_score' in match)
            self.assertTrue(0 <= match['compatibility_score'] <= 100)
        
        scores = [match['compatibility_score'] for match in matches]
        self.assertEqual(scores, sorted(scores, reverse=True))
        print("Matching functionality test passed")

def run_tests():
    suite = unittest.TestLoader().loadTestsFromTestCase(TestMarriageMatchmakingAPI)
    
    unittest.TextTestRunner(verbosity=2).run(suite)

if __name__ == '__main__':
    run_tests()