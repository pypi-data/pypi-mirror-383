#!/bin/bash

version=6.5.3

wget https://lhapdf.hepforge.org/downloads/?f=LHAPDF-${version}.tar.gz -O LHAPDF-${version}.tar.gz
tar xf LHAPDF-${version}.tar.gz

cd LHAPDF-${version}
./configure --prefix=/software/LHAPDF-${version}-install
make
make install
cd ..

rm -rf LHAPDF-{version}.tar.gz
rm -rf LHAPDF-{version}

export PATH=/software/LHAPDF-${version}-install/bin:$PATH
export LD_LIBRARY_PATH=/software/LHAPDF-${version}-install/lib:$LD_LIBRARY_PATH
export PYTHONPATH=/software/LHAPDF-${version}-install/lib/python3.10/site-packages:$PYTHONPATH

lhapdf update
lhapdf install CT10nlo
lhapdf install CT18NNLO

exit 0