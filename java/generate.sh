set -o errexit
python3 ./genbitpackingwithreducedarrayaccess.py > BitPackingWithReducedArrayAccess.java
python3 ./genbitpacking.py  > BitPacking.java
javac Unit.java
java Unit
