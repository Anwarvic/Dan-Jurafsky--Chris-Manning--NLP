import java.util.*;

public class LogConditionalObjectiveFunction {

  private LogPrior prior = new LogPrior(10.0);
  private List<Datum> data;
  public final Index featureIndex = new Index();
  public final Index labelIndex = new Index();
  
  public LogConditionalObjectiveFunction(List<Datum> data) {
    this.data = data;

    for (Datum datum : data) {
      labelIndex.add(datum.label);
      for (Object f : datum.features) {
        featureIndex.add(f);
      }
    }
  }

  public int domainDimension() {
    return featureIndex.size() * labelIndex.size();
  }

  private double[] prevX = null;

  private boolean checkCache(double[] x) {
    if (prevX == null) { return false; }

    for (int i = 0; i < prevX.length; i++) {
      if (prevX[i] != x[i]) { return false; }
    }

    return true;
  }

  private double value;
  
  public double valueAt(double[] x) {
    if (checkCache(x)) { return value; }

    prevX = new double[x.length];
    System.arraycopy(x, 0, prevX, 0, x.length);

    calculate(x);
    return value;
  }

  private double[] derivative;

  public double[] derivativeAt(double[] x) {
    if (checkCache(x)) { return derivative; }

    prevX = new double[x.length];
    System.arraycopy(x, 0, prevX, 0, x.length);

    calculate(x);
    return derivative;
  }
  
  private void calculate(double[] x) {

    value = 0.0;
    double[][] derivative = new double[labelIndex.size()][x.length/labelIndex.size()];
    double[][] weights = to2D(x);

    for (Datum datum : data) {
      double[] scores = new double[labelIndex.size()];
      for (Object feature : datum.features) {
        int f = featureIndex.indexOf(feature);
        if (f < 0) { continue; }
        for (int i = 0; i < labelIndex.size(); i++) {
          scores[i] += weights[i][f];
        }
      }

      double Z = logSum(scores);

      for (int i = 0; i < labelIndex.size(); i++) {
        double prob = Math.exp(scores[i] - Z);
        for (Object feature : datum.features) {
          int f = featureIndex.indexOf(feature);
          derivative[i][f] += prob;
          if (i == labelIndex.indexOf(datum.label)) {
            derivative[i][f]--;
          }
        }
        if (i == labelIndex.indexOf(datum.label)) {
          value -= Math.log(prob);
        }
      }
    }
    this.derivative = to1D(derivative);

    value += prior.compute(x, this.derivative);
  }
  
  public double[][] to2D(double[] x) {
    double[][] x2D = new double[labelIndex.size()][x.length/labelIndex.size()];

    int i = 0;
    for (int j = 0; j < x2D.length; j++) {
      for (int k = 0; k < x2D[j].length; k++) {
        x2D[j][k] = x[i++];
      }
    }

    return x2D;
  }

  public double[] to1D(double[][] x) {
    double[] x1D = new double[labelIndex.size() * featureIndex.size()];

    int i = 0;
    for (int j = 0; j < x.length; j++) {
      for (int k = 0; k < x[j].length; k++) {
        x1D[i++] = x[j][k];
      }
    }

    return x1D;
  }

  private static double logSum(double[] logInputs) {
    int maxIdx = 0;
    double max = logInputs[0];
    for (int i = 1; i < logInputs.length; i++) {
      if (logInputs[i] > max) {
        maxIdx = i;
        max = logInputs[i];
      }
    }
    boolean haveTerms = false;
    double intermediate = 0.0;
    double cutoff = max - 30.0;
    // we avoid rearranging the array and so test indices each time!
    for (int i = 0; i < logInputs.length; i++) {
      if (i != maxIdx && logInputs[i] > cutoff) {
        haveTerms = true;
        intermediate += Math.exp(logInputs[i] - max);
      }
    }
    if (haveTerms) {
      return max + Math.log(1.0 + intermediate);
    } else {
      return max;
    }
  }

}