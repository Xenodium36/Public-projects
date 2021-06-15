package ija.project;

import com.fasterxml.jackson.annotation.JsonIgnore;

import java.util.ArrayList;
import java.util.List;

/**
 * Defining path for carts
 * Contains list of coordinates, which takes cart
 */
public class Path {
    private List<Coordinate> path = new ArrayList<>();

    public Path() {}

    public Path(List<Coordinate> path) {
        this.path = path;
    }

    public List<Coordinate> getPath() {
        return path;
    }

    public void setPath(List<Coordinate> path) {
        this.path = path;
    }

    public void addToPath(List<Coordinate> path){
        this.path.addAll(path);
    }

    private double getDistance(Coordinate a, Coordinate b){
        return Math.sqrt(Math.pow(a.getX() - b.getX(), 2) + Math.pow(a.getY() - b.getY(), 2));
    }

    /**
     * @param distance Driven distance by cart on path
     * @return new coordinates, where cart should be drawn
     */
    public Coordinate getCoordinateByDistance(double distance){
        double length = 0;
        Coordinate a = null;
        Coordinate b = null;
        for(int i = 0; i < path.size() - 1; i++){
            a = path.get(i);
            b = path.get(i + 1);
            if (length + getDistance(a,b) >= distance){
                break;
            }
            length +=getDistance(a,b);
        }
        if (a == null || b == null){
            return null;
        }

        double driven = (distance - length)/getDistance(a,b);
        return new Coordinate(a.getX() + (b.getX() - a.getX()) * driven, a.getY() + (b.getY() - a.getY()) * driven);
    }

    /**
     *
     * @return length of whole path, that cart should drive
     */
    @JsonIgnore
    public double getPathSize(){
        double size = 0;
        for(int i = 0; i < path.size() - 1; i++){
            size += getDistance(path.get(i), path.get(i+1));
        }
        return size;
    }
}
