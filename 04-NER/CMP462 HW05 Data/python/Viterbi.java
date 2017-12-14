import java.util.*;

public class Viterbi {

	private final Index labelIndex;
	private final Index featureIndex;
	private final double[][] weights;

	public Viterbi(Index labelIndex, Index featureIndex, double[][] weights) {
		this.labelIndex = labelIndex;
		this.featureIndex = featureIndex;
		this.weights = weights;
	}

	public void decode(List<Datum> data, List<Datum> dataWithMultiplePrevLabels) {
		// load words from the data
		List<String> words = new ArrayList<String>();
		for (Datum datum : data) {
			words.add(datum.word);
		}

		int[][] backpointers = new int[data.size()][numLabels()];
		double[][] scores = new double[data.size()][numLabels()];

		int prevLabel = labelIndex.indexOf(data.get(0).previousLabel);
		double[] localScores = computeScores(data.get(0).features);

		int position = 0;
		for (int currLabel = 0; currLabel < localScores.length; currLabel++) {
			backpointers[position][currLabel] = prevLabel;
			scores[position][currLabel] = localScores[currLabel];
		}

		// for each position in data
		for (position = 1; position< data.size(); position++) {
			// equivalent position in dataWithMultiplePrevLabels
			int i = position * numLabels() - 1; 
			
			// for each previous label 
			for (int j = 0; j < numLabels(); j++) {
				Datum datum = dataWithMultiplePrevLabels.get(i + j);
				String previousLabel = datum.previousLabel;
				prevLabel = labelIndex.indexOf(previousLabel);

				localScores = computeScores(datum.features);
				for (int currLabel = 0; currLabel < localScores.length; currLabel++) {
					double score = localScores[currLabel]
							+ scores[position - 1][prevLabel];
					if (prevLabel == 0 || score > scores[position][currLabel]) {
						backpointers[position][currLabel] = prevLabel;
						scores[position][currLabel] = score;
					}
				}
			}
		}

		int bestLabel = 0;
		double bestScore = scores[data.size() - 1][0];

		for (int label = 1; label < scores[data.size() - 1].length; label++) {
			if (scores[data.size() - 1][label] > bestScore) {
				bestLabel = label;
				bestScore = scores[data.size() - 1][label];
			}
		}

		for (position = data.size() - 1; position >= 0; position--) {
			Datum datum = data.get(position);
			datum.guessLabel = (String) labelIndex.get(bestLabel);
			bestLabel = backpointers[position][bestLabel];
		}

	}

	private double[] computeScores(List<String> features) {

		double[] scores = new double[numLabels()];

		for (Object feature : features) {
			int f = featureIndex.indexOf(feature);
			if (f < 0) {
				continue;
			}
			for (int i = 0; i < scores.length; i++) {
				scores[i] += weights[i][f];
			}
		}

		return scores;
	}

	private int numLabels() {
		return labelIndex.size();
	}

}