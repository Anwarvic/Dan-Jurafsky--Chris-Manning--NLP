public class LogPrior {

  public LogPrior(double sigma) {
    this.sigma = sigma;
  }

  private double sigma;

  public double compute(double[] x, double[] grad) {
    double val = 0.0;

    for (int i = 0; i < x.length; i++) {
      val += x[i] * x[i] / 2.0 / (sigma*sigma);
      grad[i] += x[i] / (sigma*sigma);
    }
    return val;
  }

}
