wget https://github.com/DanBloomberg/leptonica/releases/download/1.79.0/leptonica-1.79.0.tar.gz
tar xzf leptonica-1.79.0.tar.gz
cd leptonica-1.79.0
./configure
make
sudo make install
cd ..
sudo apt-get install libtiff5 libtiffxx5 zlib1g
wget https://github.com/tesseract-ocr/tesseract/archive/4.1.1.tar.gz
tar xzf 4.1.1.tar.gz
cd tesseract-4.1.1
bash ./autogen.sh
./configure
make 
sudo make install
cd ..
