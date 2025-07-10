import schedule
import time
import threading
import datetime
from services import trade_logic, etf_strategies
from utils.logger import log_message, get_logs

# --- Methods to run ---
def task_0930():
    log_message(f"[{datetime.datetime.now()}] ⏰ Running 9:30 AM task NASDAQ_and_MON100")
    etf_strategies.NASDAQ_and_MON100()

def task_1305():
    log_message(f"[{datetime.datetime.now()}] ⏰ Running 1:05 PM task etf_daily_strategy_sell")
    etf_strategies.etf_daily_strategy_sell()

def task_1512():
    log_message(f"[{datetime.datetime.now()}] ⏰ Running 3:12 PM task etf_daily_strategy_buy")
    etf_strategies.etf_daily_strategy_buy()
    log_message(f"[{datetime.datetime.now()}] ⏰ Running 3:12 PM task etf_longterm_nifty50_strategy")
    etf_strategies.etf_longterm_nifty50_strategy()

# --- Weekday check wrapper ---
def run_if_weekday(task):
    def wrapper():
        today = datetime.datetime.today().weekday()  # 0=Mon, ..., 6=Sun
        if today < 5:  # Mon to Fri
            task()
        else:
            log_message(f"[{datetime.datetime.now()}] ❌ Skipping {task.__name__} (Weekend)")
    return wrapper

# --- Schedule tasks ---
schedule.every().day.at("09:30").do(run_if_weekday(task_0930))
schedule.every().day.at("13:05").do(run_if_weekday(task_1305))
schedule.every().day.at("15:12").do(run_if_weekday(task_1512))

# --- Scheduler loop ---
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# --- Run in background thread or main ---
if __name__ == "__main__":
    log_message("📅 Scheduler started. Running on weekdays only.")
    scheduler_thread = threading.Thread(target=run_scheduler)
    scheduler_thread.daemon = True
    scheduler_thread.start()

    # Keep main thread alive
    while True:
        time.sleep(60)