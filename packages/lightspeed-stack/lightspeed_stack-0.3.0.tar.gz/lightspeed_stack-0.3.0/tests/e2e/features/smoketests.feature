Feature: Smoke tests


  Background:
    Given The service is started locally
      And REST API service hostname is localhost
      And REST API service port is 8080
      And REST API service prefix is /v1


  Scenario: Check if the main endpoint is reachable
    Given The system is in default state
     When I access endpoint "/" using HTTP GET method
     Then The status code of the response is 200
      And Content type of response should be set to "text/html"
