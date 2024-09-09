from flask import Blueprint, render_template, redirect

from .. import redis_rq

from pipek.jobs import hello_rq

module = Blueprint("rq-test", __name__, url_prefix="/rq-test")


@module.route("/")
def index():
    job = redis_rq.redis_queue.queue.enqueue(
        hello_rq.say_hello_rq,
        args=("thanathip",),
        job_id=f"hello-01",
        timeout=600,
        job_timeout=600,
    )

    return f"Hello world {job.id}"


@module.route("/state")
def check_job_state():

    job = redis_rq.redis_queue.get_job("hello-01")
    return f"Hello world {job.id} {job.result}"
