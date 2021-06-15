package ija.project;

import org.jgrapht.graph.DefaultWeightedEdge;
import org.jgrapht.graph.SimpleWeightedGraph;

import java.util.*;

public class Graph {
    private SimpleWeightedGraph<Coordinate, DefaultWeightedEdge> graph = new SimpleWeightedGraph<>(DefaultWeightedEdge.class);
    private static final Coordinate start = new Coordinate(660,260);
    private static final Coordinate end = new Coordinate(100,260);
    private static Map<String, Coordinate> stopStations;

    /**
     *  initialize all the stop stations
     */
    public Graph() {
        setStopStations();
    }

    /**
     * @return graph
     */
    public SimpleWeightedGraph<Coordinate, DefaultWeightedEdge> getGraph() {
        return graph;
    }

    /**
     * to return start coordinates
     * @return start coordinates
     */
    public Coordinate getStart() {
        return start;
    }

    /**
     * to return end coordinates
     * @return end coordinates
     */
    public Coordinate getEnd() {
        return end;
    }

    /**
     * all coordinates inputed to the map
     * @return map out of unique name (key:string) and coordinates (value:coordinates)
     */
    public static Map<String, Coordinate> setStopStations(){
        Map<String, Coordinate> outMap = new HashMap<>();

        outMap.put("I0", new Coordinate(620,20));
        outMap.put("I1", new Coordinate(620,60));
        outMap.put("I2", new Coordinate(620,100));
        outMap.put("I3", new Coordinate(620,140));
        outMap.put("I4", new Coordinate(620,180));
        outMap.put("I5", new Coordinate(620,220));
        outMap.put("I6", new Coordinate(620,260));
        outMap.put("I7", new Coordinate(620,300));
        outMap.put("I8", new Coordinate(620,340));
        outMap.put("I9", new Coordinate(620,380));
        outMap.put("I10", new Coordinate(620,420));
        outMap.put("I11", new Coordinate(620,460));
        outMap.put("I12", new Coordinate(620,500));

        outMap.put("J0", new Coordinate(540,20));
        outMap.put("J1", new Coordinate(540,60));
        outMap.put("J2", new Coordinate(540,100));
        outMap.put("J3", new Coordinate(540,140));
        outMap.put("J4", new Coordinate(540,180));
        outMap.put("J5", new Coordinate(540,220));
        outMap.put("J6", new Coordinate(540,260));
        outMap.put("J7", new Coordinate(540,300));
        outMap.put("J8", new Coordinate(540,340));
        outMap.put("J9", new Coordinate(540,380));
        outMap.put("J10", new Coordinate(540,420));
        outMap.put("J11", new Coordinate(540,460));
        outMap.put("J12", new Coordinate(540,500));

        outMap.put("K0", new Coordinate(460,20));
        outMap.put("K1", new Coordinate(460,60));
        outMap.put("K2", new Coordinate(460,100));
        outMap.put("K3", new Coordinate(460,140));
        outMap.put("K4", new Coordinate(460,180));
        outMap.put("K5", new Coordinate(460,220));
        outMap.put("K6", new Coordinate(460,260));
        outMap.put("K7", new Coordinate(460,300));
        outMap.put("K8", new Coordinate(460,340));
        outMap.put("K9", new Coordinate(460,380));
        outMap.put("K10", new Coordinate(460,420));
        outMap.put("K11", new Coordinate(460,460));
        outMap.put("K12", new Coordinate(460,500));

        outMap.put("L0", new Coordinate(380,20));
        outMap.put("L1", new Coordinate(380,60));
        outMap.put("L2", new Coordinate(380,100));
        outMap.put("L3", new Coordinate(380,140));
        outMap.put("L4", new Coordinate(380,180));
        outMap.put("L5", new Coordinate(380,220));
        outMap.put("L6", new Coordinate(380,260));
        outMap.put("L7", new Coordinate(380,300));
        outMap.put("L8", new Coordinate(380,340));
        outMap.put("L9", new Coordinate(380,380));
        outMap.put("L10", new Coordinate(380,420));
        outMap.put("L11", new Coordinate(380,460));
        outMap.put("L12", new Coordinate(380,500));

        outMap.put("M0", new Coordinate(300,20));
        outMap.put("M1", new Coordinate(300,60));
        outMap.put("M2", new Coordinate(300,100));
        outMap.put("M3", new Coordinate(300,140));
        outMap.put("M4", new Coordinate(300,180));
        outMap.put("M5", new Coordinate(300,220));
        outMap.put("M6", new Coordinate(300,260));
        outMap.put("M7", new Coordinate(300,300));
        outMap.put("M8", new Coordinate(300,340));
        outMap.put("M9", new Coordinate(300,380));
        outMap.put("M10", new Coordinate(300,420));
        outMap.put("M11", new Coordinate(300,460));
        outMap.put("M12", new Coordinate(300,500));

        outMap.put("N0", new Coordinate(220,20));
        outMap.put("N1", new Coordinate(220,60));
        outMap.put("N2", new Coordinate(220,100));
        outMap.put("N3", new Coordinate(220,140));
        outMap.put("N4", new Coordinate(220,180));
        outMap.put("N5", new Coordinate(220,220));
        outMap.put("N6", new Coordinate(220,260));
        outMap.put("N7", new Coordinate(220,300));
        outMap.put("N8", new Coordinate(220,340));
        outMap.put("N9", new Coordinate(220,380));
        outMap.put("N10", new Coordinate(220,420));
        outMap.put("N11", new Coordinate(220,460));
        outMap.put("N12", new Coordinate(220,500));

        outMap.put("O0", new Coordinate(140,20));
        outMap.put("O1", new Coordinate(140,60));
        outMap.put("O2", new Coordinate(140,100));
        outMap.put("O3", new Coordinate(140,140));
        outMap.put("O4", new Coordinate(140,180));
        outMap.put("O5", new Coordinate(140,220));
        outMap.put("O6", new Coordinate(140,260));
        outMap.put("O7", new Coordinate(140,300));
        outMap.put("O8", new Coordinate(140,340));
        outMap.put("O9", new Coordinate(140,380));
        outMap.put("O10", new Coordinate(140,420));
        outMap.put("O11", new Coordinate(140,460));
        outMap.put("O12", new Coordinate(140,500));

        stopStations = outMap;

        return outMap;
    }

    /**
     * this function creates graph for all coordinates
     * if coordinate is disabled does not create edge
     */
    public void createGraph(){
        this.graph = null;
        this.graph = new SimpleWeightedGraph<>(DefaultWeightedEdge.class);

        Map<String, Coordinate> coordinateMap = stopStations;

        graph.addVertex(start);
        graph.addVertex(end);

        for (Coordinate coord : coordinateMap.values()) {
            graph.addVertex(coord);
        }

        for (char c = 'I'; c <= 'O'; c++ ) {
            for (int i = 0; i <= 12; i++) {
                String sourceName = "" + c + i;
                Coordinate source = coordinateMap.get(sourceName);

                if (!source.isEnabled())
                    continue;

                if ( i < 12 ) {
                    String targetName = "" + c + (i + 1);
                    Coordinate target = coordinateMap.get(targetName);

                    if (target.isEnabled()) {
                        graph.addEdge(source, target);
                        if (i == 6) {
                            if (c == 'I') {
                                graph.addEdge(source, start);
                            } else if ( c == 'O') {
                                graph.addEdge(source, end);
                            }
                        }
                    }
                    if (i % 6 == 0 && c != 'O') {
                        targetName = "" + ((char)((int)c + 1)) + i;
                        target = coordinateMap.get(targetName);
                        if (target.isEnabled()) {
                            graph.addEdge(source, target);
                        }
                    }
                }else if (c != 'O'){
                    String targetName = "" + ((char)((int)c + 1)) + i;
                    Coordinate target = coordinateMap.get(targetName);
                    if (target.isEnabled()) {
                        graph.addEdge(source, target);
                    }

                }
            }
        }
    }

    /**
     * Find center coordinates for cart station from given coordinates
     * @param coordinate - coordinate from which we try finding the stop station
     * @return - coordinate of cart station
     */
    public static Coordinate getStopByCoords(Coordinate coordinate){
        if (stopStations == null)
            return null;

        for (Coordinate coord : stopStations.values()) {
            if (Math.abs(coordinate.getX() - coord.getX()) <= 3){
                if (Math.abs(coordinate.getY() - coord.getY()) <= 3){
                    return coord;
                }
            }
        }

        return null;
    }
}
