package ija.project;


import javafx.event.EventHandler;
import javafx.scene.input.MouseEvent;
import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Line;
import javafx.scene.shape.Shape;

import java.time.LocalTime;
import java.util.ArrayList;
import java.util.List;

/**
 * Defining cart
 * cart: has speed, at which it drives
 *       driven distance
 *       path, which it takes
 *       actual coordinates
 */

public class Cart implements Drawable, TimeUpdate{

    private Coordinate position;
    private double speed = 5;
    private double distance = 0;
    private Path path;
    private List<Shape> gui;
    private Circle circle;
    public List<Coordinate> stops;
    private double tmpSpeed = 5;
    private LocalTime stopTime = LocalTime.now();
    private Cart(){}
    private Controller controller;

	/**
	*Creates mouseEvent for cart, so it can display path for cart
	*/
    public void setClickedEvent(){
        circle.setOnMouseClicked(new EventHandler<MouseEvent>() {
            @Override
            public void handle(MouseEvent mouseEvent) {
                controller.cartPathLines.clear();
                controller.textAreaDetails.setText(stops.toString());
                Line tmpLine;
                for(int i = 0; i < path.getPath().size() - 1; i++){
                    tmpLine = new Line(path.getPath().get(i).getX(), path.getPath().get(i).getY(),
                            path.getPath().get(i + 1).getX(), path.getPath().get(i + 1).getY());
                    tmpLine.setStroke(Color.GREEN);
                    tmpLine.setStrokeWidth(3.0);
                    controller.cartPathLines.add(tmpLine);
                }
                controller.refreshPane();
            }
        });
    }

    /**
     * cart initialization
     * @param position - starting position of the cart
     * @param speed - starting speed of the cart
     * @param path - some passed path
     * @param stops - list of passed stops
     * @param c - controller for todo
     */
    public Cart(Coordinate position, double speed, Path path, List<Coordinate> stops, Controller c) {
        this.position = position;
        this.speed = speed;
        this.tmpSpeed = speed;
        this.path = path;
        this.stops = stops;
        this.controller = c;
        setGui();
    }

    /**
     * This function moves carts ath the map
     * @param coordinate Coordinates, where object should be moved
     */
    private void moveGui(Coordinate coordinate){
        for (Shape shape : gui){
            shape.setTranslateX((coordinate.getX() - position.getX()) + shape.getTranslateX());
            shape.setTranslateY((coordinate.getY() - position.getY()) + shape.getTranslateY());
        }
    }

    /**
     * This adds new cart to gui with radius 5, and Green color
     */
    private void setGui(){
        gui = new ArrayList<>();
        circle = new Circle(position.getX(), position.getY(), 6, Color.BLUE);
        setClickedEvent();
        gui.add(circle);
    }

    /**
     *
     * @return Path - carts path
     */
    public Path getPath() {
        return path;
    }

    /**
     *
     * @return List of shapes
     */
    @Override
    public List<Shape> getGUI() {
        return gui;
    }

    /**
     * Getting driven distance of cart, and setting new coordinates of cart, when it moves
     *
     */
    @Override
    public void update(LocalTime time){

        // if stop was found and current location of cart == stop position
        if (stops.size() > 0 && (position.checkIfEquals(new Coordinate(stops.get(0).getX() + 40,
                stops.get(0).getY())) || position.checkIfEquals(new Coordinate(stops.get(0).getX() - 40,
                stops.get(0).getY())))){

            tmpSpeed = speed;
            speed = 0;
            stopTime = time;
            stops.remove(0);
        }

        if(speed == 0 && stopTime.plusSeconds((long) 0.5).isBefore(time)){
            speed = tmpSpeed;
        }

        distance += speed;

        if (distance > path.getPathSize()){
            Coordinate tmp = path.getCoordinateByDistance(path.getPathSize());
            moveGui(tmp);
            position = tmp;
            return;
        }

        Coordinate coords = path.getCoordinateByDistance(distance);

        moveGui(coords);
        position = coords;
    }

}
