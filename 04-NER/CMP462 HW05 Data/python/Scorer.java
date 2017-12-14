import java.util.*;

public class Scorer {

  public static void score(List<Datum> data) {

    Set<Pair> trueEntities = new HashSet();
    Set<Pair> guessEntities = new HashSet();
    
    String prevLabel = "O";
    int start = 0;

    for (int i = 0; i < data.size(); i++) {
      String label = data.get(i).label;

      if (label.equals("PERSON") && prevLabel.equals("O")) {
        start = i;        
      } else if (label.equals("O") && prevLabel.equals("PERSON")) {
        Pair p = new Pair(start, i);
        trueEntities.add(p);
      }

      prevLabel = label;
    }

    prevLabel = "O";
    
    for (int i = 0; i < data.size(); i++) {
      String label = data.get(i).guessLabel;

      if (label.equals("PERSON") && prevLabel.equals("O")) {
        start = i;        
      } else if (label.equals("O") && prevLabel.equals("PERSON")) {
        Pair p = new Pair(start, i);
        guessEntities.add(p);
      }

      prevLabel = label;
    }

    Set<Pair> s = new HashSet(trueEntities);
    s.retainAll(guessEntities);

    int tp = s.size();

    double prec = (double)tp / (double)guessEntities.size();
    double recall = (double)tp / (double)trueEntities.size();
    double f = (2 * prec * recall) / (prec + recall);

    System.out.println("precision = "+prec);
    System.out.println("recall = "+recall);
    System.out.println("F1 = "+f);
  }

  private static class Pair {
    int first;
    int second;

    public Pair(int first, int second) {
      this.first = first;
      this.second = second;
    }
    
    public int hashCode() {
      return (first << 16) ^ second;
    }

    public boolean equals(Object o) {
      if (!(o instanceof Pair)) { return false; }
      Pair p = (Pair)o;
      return (first == p.first && second == p.second);
    }

    public String toString() { return "("+first+", "+second+")"; }
  }
  
}