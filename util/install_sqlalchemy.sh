cd $STPOL_DIR
wget --no-check-certificate https://pypi.python.org/packages/source/S/SQLAlchemy/SQLAlchemy-0.8.1.tar.gz
tar xf SQLAlchemy-0.8.1.tar.gz
mkdir local
cd SQLAlchemy-0.8.1
python setup.py install --prefix=$STPOL_DIR/local
