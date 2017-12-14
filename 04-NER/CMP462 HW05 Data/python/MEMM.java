import java.util.*;
import java.io.*;

import org.json.JSONException;
import org.json.JSONObject;
import org.json.JSONTokener;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;


public class MEMM {

	public static void main(String[] args) throws IOException {

		boolean print = false;
		boolean submit = false;

		if (args.length > 2) {
		    if (args[2].equals("-print")) {
			print = true;
		    } else if (args[2].equals("-submit")) {
			submit = true;
		    }
		}

		List<Datum> testData = runMEMM(args[0], args[1]);

		// print words + guess labels for development
		if (print) {
			for (Datum datum : testData) {
			    System.out.println(base64decode(datum.word) + "\t" + datum.label + "\t"
						+ datum.guessLabel);
			}
		}

		// print guess labels to submit 
		if (submit) {
			for (Datum datum : testData) {
			    System.out.println("+++" + base64decode(datum.word) + "\t" + datum.guessLabel);
			}
			return;
		}

		System.out.println();
		Scorer.score(testData);

	}


    public static List<Datum> runMEMM(String trainFile, String testFile) throws IOException{

		List<Datum> trainData = readData(trainFile);
		List<Datum> testDataWithMultiplePrevLabels = readData(testFile);
		

		LogConditionalObjectiveFunction obj = new LogConditionalObjectiveFunction(
				trainData);
		double[] initial = new double[obj.domainDimension()];

		// restore the original test data from the source
		List<Datum> testData = new ArrayList<Datum>();
		testData.add(testDataWithMultiplePrevLabels.get(0));
		for (int i = 1; i < testDataWithMultiplePrevLabels.size(); i += obj.labelIndex.size()) {
			testData.add(testDataWithMultiplePrevLabels.get(i));
		}

		QNMinimizer minimizer = new QNMinimizer(15);
		double[][] weights = obj.to2D(minimizer.minimize(obj, 1e-4, initial,
				-1, null));

		Viterbi viterbi = new Viterbi(obj.labelIndex, obj.featureIndex, weights);
		viterbi.decode(testData, testDataWithMultiplePrevLabels);

		return testData;
	}

	// Read words, labels, and features
	private static List<Datum> readData(String filename) throws IOException {
		List<Datum> data = new ArrayList<Datum>();
		// read the JSON file
		FileInputStream fstream = new FileInputStream(filename);
		JSONTokener tokener = null;

		try {
			tokener = new JSONTokener(fstream);
			while (tokener.more()) {
				JSONObject object = (JSONObject) tokener.nextValue();
				if (object == null) {
					break;
				}

				String word = object.getString("_word");
				String label = object.getString("_label");
				String previousLabel = object.getString("_prevLabel");

				JSONObject featureObject = (JSONObject) object.get("_features");
				List<String> features = new ArrayList<String>();
				for (String name : JSONObject.getNames(featureObject)) {
					features.add(featureObject.getString(name));
				}

				Datum datum = new Datum(word, label);
				datum.features = features;
				datum.previousLabel = previousLabel;

				data.add(datum);
			}
		} catch (JSONException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}

		return data;
	}

    private static String base64decode(String str) {
	Base64 base = new Base64();
	byte[] strBytes = str.getBytes();
	byte[] decodedBytes = base.decode(strBytes);
	String decoded = new String(decodedBytes);
	return decoded;
    }
}