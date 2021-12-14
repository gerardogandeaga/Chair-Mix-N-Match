# pull input data and models from google drive
wget -O ./data.tar.gz "https://www.dropbox.com/s/qfq684igev9j8mm/data.tar.gz?dl=1"
tar -xzf data.tar.gz
mv models ./scorer/

rm -f data.tar.gz

# setup python environment
python3 -m venv venv
source ./venv/bin/activate
python3 -m pip install --upgrade pip
pip install -r requirements.txt