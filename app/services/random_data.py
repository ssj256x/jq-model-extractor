def get_large_random_data_json():
    return '''
{
  "id": "usr_9f3a21c4",
  "profile": {
    "name": {
      "first": "Aarav",
      "middle": null,
      "last": "Sharma"
    },
    "age": 32,
    "contact": {
      "email": "aarav.sharma@example.com",
      "phone": {
        "countryCode": "+91",
        "number": "9876543210",
        "verified": true
      }
    },
    "addresses": [
      {
        "type": "home",
        "primary": true,
        "location": {
          "street": "12 MG Road",
          "city": "Bengaluru",
          "state": "Karnataka",
          "country": "India",
          "postalCode": "560001"
        },
        "geo": {
          "lat": 12.9716,
          "lng": 77.5946
        }
      },
      {
        "type": "office",
        "primary": false,
        "location": {
          "street": "4th Block, Koramangala",
          "city": "Bengaluru",
          "state": "Karnataka",
          "country": "India",
          "postalCode": "560095"
        },
        "geo": {
          "lat": 12.9352,
          "lng": 77.6245
        }
      }
    ]
  },
  "account": {
    "createdAt": "2023-11-18T09:45:23Z",
    "status": "ACTIVE",
    "preferences": {
      "language": "en",
      "currency": "INR",
      "notifications": {
        "email": true,
        "sms": false,
        "push": {
          "enabled": true,
          "quietHours": {
            "from": "22:00",
            "to": "07:00"
          }
        }
      }
    }
  },
  "subscriptions": [
    {
      "id": "sub_basic_001",
      "plan": "BASIC",
      "billing": {
        "cycle": "MONTHLY",
        "price": 499,
        "tax": {
          "rate": 0.18,
          "amount": 89.82
        },
        "nextBillingDate": "2025-01-15"
      },
      "features": [
        "standard-support",
        "basic-analytics"
      ]
    },
    {
      "id": "sub_premium_002",
      "plan": "PREMIUM",
      "billing": {
        "cycle": "YEARLY",
        "price": 4999,
        "tax": {
          "rate": 0.18,
          "amount": 899.82
        },
        "nextBillingDate": "2025-11-18"
      },
      "features": [
        "priority-support",
        "advanced-analytics",
        "custom-reports"
      ]
    }
  ],
  "audit": {
    "createdBy": "system",
    "createdAt": "2023-11-18T09:45:23Z",
    "lastUpdated": {
      "by": "admin_102",
      "at": "2024-12-02T14:11:09Z",
      "changes": [
        {
          "field": "account.status",
          "oldValue": "PENDING",
          "newValue": "ACTIVE"
        },
        {
          "field": "profile.contact.phone.verified",
          "oldValue": false,
          "newValue": true
        }
      ]
    }
  }
}
'''
