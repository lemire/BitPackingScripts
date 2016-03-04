
import java.text.DecimalFormat;
import java.util.Arrays;
import java.util.Random;


public class BenchmarkBitPacking {

        private static void test(boolean verbose) {
                DecimalFormat dfspeed = new DecimalFormat("0");
                final int N = 32;
                final int times = 100000;
                Random r = new Random(0);
                int[] data = new int[N];
                int[] compressed = new int[N];
                int[] uncompressed = new int[N];
                for (int bit = 0; bit < 31; ++bit) {
                        long comp = 0;
                        long compwm = 0;
                        long decomp = 0;
                        long decompwr = 0;
                        for (int t = 0; t < times; ++t) {
                                for (int k = 0; k < N; ++k) {
                                        data[k] = r.nextInt(1 << bit);
                                }
                                long time1 = System.nanoTime();
                                BitPacking
                                        .fastpack(data, 0, compressed, 0, bit);
                                long time2 = System.nanoTime();
                                BitPacking.fastpackwithoutmask(data, 0,
                                        compressed, 0, bit);
                                long time3 = System.nanoTime();
                                BitPacking.fastunpack(compressed, 0,
                                        uncompressed, 0, bit);
                                long time4 = System.nanoTime();
                                BitPackingWithReducedArrayAccess.fastunpack(compressed, 0,
                                        uncompressed, 0, bit);
                                long time5 = System.nanoTime();

                                comp += time2 - time1;
                                compwm += time3 - time2;
                                decomp += time4 - time3;
                                decompwr += time5 - time4;
                        }
                        if (verbose)
                                System.out.println("bit = "
                                        + bit
                                        + " comp. speed = "
                                        + dfspeed.format(N * times * 1000.0
                                                / (comp))
                                        + " comp. speed wm = "
                                        + dfspeed.format(N * times * 1000.0
                                                / (compwm))
                                        + " decomp. speed = "
                                        + dfspeed.format(N * times * 1000.0
                                                / (decomp))
                                                + " decomp. speed (r.a.a.) = "
                                                + dfspeed.format(N * times * 1000.0
                                                        / (decompwr))

                                                );
                }
        }

        /**
         * Main method
         *
         * @param args
         *                command-line arguments
         */
        public static void main(String[] args) {
                System.out.println("Testing packing ");
                test(false);
                test(true);
        }

}
