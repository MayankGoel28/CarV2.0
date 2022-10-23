pkill -f streamlit
pkill -f streamlit
pkill -f python3
streamlit run runner.py 1 vehicle4.json &
streamlit run runner.py 1 vehicle2.json &
python3 runner.py 0 vehicle3.json &
python3 runner.py 0 vehicle1.json &
