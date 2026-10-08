import json
import logging
import os
import random
import time

from fastapi import FastAPI, HTTPException, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = FastAPI(title="dicey")
logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("dicey")

FAIL_RATE = float(os.getenv("FAIL_RATE", "0"))  # 0.0 - 1.0, used to simulate errors

ROLLS = Counter("dicey_rolls_total", "Dice rolls by outcome", ["outcome"])
LATENCY = Histogram("dicey_roll_seconds", "Time spent rolling the dice")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/roll")
def roll():
    with LATENCY.time():
        time.sleep(random.uniform(0.005, 0.05))
        if random.random() < FAIL_RATE:
            ROLLS.labels(outcome="error").inc()
            log.info(json.dumps({"event": "roll", "status": "error"}))
            raise HTTPException(status_code=500, detail="the dice fell off the table")
        result = random.randint(1, 6)
    ROLLS.labels(outcome="ok").inc()
    log.info(json.dumps({"event": "roll", "status": "ok", "result": result}))
    return {"result": result}


@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)