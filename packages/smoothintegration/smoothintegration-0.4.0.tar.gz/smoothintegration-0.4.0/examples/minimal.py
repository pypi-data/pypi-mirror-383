import os
import uuid

from flask import Flask, redirect

import smoothintegration

# Your Client Secret should be kept safe, so make sure to store it in a secure location
smoothintegration.client_id = "your-smooth-integration-client-id" # TODO: replace with your client id
smoothintegration.client_secret = "your-smooth-integration-client-secret" # TODO: replace with your client secret

# Change this to a company ID you've created in the SmoothIntegration dashboard.
# Alternatively, you can create a net Company with the smoothintegration.companies.create_company method
demo_company_id: uuid.UUID = uuid.UUID("your-smooth-integration-company-id") # TODO: replace with your company id

# For this example we use Flask, but you can use any web framework
app = Flask(__name__)

# Example endpoint, this allows your end-users to connect their accounting system, in this case Exact.
@app.route("/connect-exact")
def connect_exact():
    url = smoothintegration.exact.get_consent_url(
        company_id=demo_company_id,
        version="uk",
    )
    return redirect(url)


if __name__ == "__main__":
    # Start the Flask server
    app.run(port=int(os.environ.get("PORT", 8080)))
    print("Server running, connect Exact at http://localhost:8080/connect-exact")

    # Stream CDC events
    for event in smoothintegration.data.cdc.stream(from_event_id='0'):
        print(event['event'], event['document']['id'], event['document']['status'])
        # This is where you would update your datastore using the incoming event
