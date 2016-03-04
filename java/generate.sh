set -o errexit
python3 ./genbitpacking64.py > BitPacking64.java
python3 ./genbitpackingwithreducedarrayaccess.py > BitPackingWithReducedArrayAccess.java
python3 ./genbitpacking.py  > BitPacking.java
javac Unit.java
java Unit

echo "Considering typing javac BenchmarkBitPacking.java && java BenchmarkBitPacking "
