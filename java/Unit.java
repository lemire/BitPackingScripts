import java.util.*;

public class Unit {

    public static void verifyBitPacking() {
        System.out.println("verifying BitPacking");
        final int N = 32;
        final int TIMES = 1000;
        Random r = new Random();
        int[] data = new int[N];
        int[] compressed = new int[N];
        int[] uncompressed = new int[N];
        for (int bit = 0; bit < 31; ++bit) {
            for (int t = 0; t < TIMES; ++t) {
                for (int k = 0; k < N; ++k) {
                    data[k] = r.nextInt(1 << bit);
                }
                BitPacking.fastpack(data, 0, compressed, 0, bit);
                BitPacking.fastunpack(compressed, 0, uncompressed, 0, bit);
                if(!Arrays.equals(uncompressed, data)) throw new RuntimeException("bug");
            }
        }
        System.out.println("ok");

    }
    public static void verifyBitPackingWithReducedArrayAccess() {
        System.out.println("verifying BitPackingWithReducedArrayAccess");
        final int N = 32;
        final int TIMES = 1000;
        Random r = new Random();
        int[] data = new int[N];
        int[] compressed = new int[N];
        int[] uncompressed = new int[N];
        for (int bit = 0; bit < 31; ++bit) {
            for (int t = 0; t < TIMES; ++t) {
                for (int k = 0; k < N; ++k) {
                    data[k] = r.nextInt(1 << bit);
                }
                BitPackingWithReducedArrayAccess.fastpack(data, 0, compressed, 0, bit);
                BitPackingWithReducedArrayAccess.fastunpack(compressed, 0, uncompressed, 0, bit);
                if(!Arrays.equals(uncompressed, data)) throw new RuntimeException("bug");
            }
        }
        System.out.println("ok");

    }

    public static void main(String[] args) {
        verifyBitPacking();
        verifyBitPackingWithReducedArrayAccess();
    }
}
