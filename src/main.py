# initialize our Flask application
from logging import getLogger, DEBUG

from flask import Flask, request, jsonify, render_template, Response

from commons import VERSION_NUMBER, LOG_LOCATION
from components.actions.base.action import am
from components.events.base.event import em
from components.logs.log_event import LogEvent
from components.schemas.trading import Order, Position
from utils.log import get_logger
from utils.register import register_action, register_event, register_link

# register actions, events, links
from settings import REGISTERED_ACTIONS, REGISTERED_EVENTS, REGISTERED_LINKS

registered_actions = [register_action(action) for action in REGISTERED_ACTIONS]
registered_events = [register_event(event) for event in REGISTERED_EVENTS]
registered_links = [register_link(link, em, am) for link in REGISTERED_LINKS]

app = Flask(__name__)

# configure logging
logger = get_logger(__name__)

schema_list = {
    'order': Order().as_json(),
    'position': Position().as_json()
}


@app.route("/", methods=["GET"])
def dashboard():
    if request.method == 'GET':
        action_list = am.get_all()
        return render_template(
            template_name_or_list='dashboard.html',
            schema_list=schema_list,
            action_list=action_list,
            event_list=registered_events,
            version=VERSION_NUMBER
        )


@app.route("/webhook", methods=["POST"])
def webhook():
    if request.method == 'POST':
        logger.info(f'Request Data: {request.get_json()}')
        triggered_events = []
        for event in em.get_all():
            if event.webhook:
                if event.key == request.get_json()['key']:
                    event.trigger(data=request.get_json())
                    triggered_events.append(event.name)

        if not triggered_events:
            logger.warning(f'No events triggered for webhook request {request.get_json()}')
        else:
            logger.info(f'Triggered events: {triggered_events}')

    return Response(status=200)


@app.route("/logs", methods=["GET"])
def get_logs():
    if request.method == 'GET':
        log_file = open(LOG_LOCATION, 'r')
        logs = [LogEvent().from_line(log) for log in log_file.readlines()]
        return jsonify([log.as_json() for log in logs])


if __name__ == '__main__':
    app.run(debug=True)
