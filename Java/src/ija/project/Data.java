package ija.project;

import java.util.List;

/**
 * Temporary, used to read carts from yml file.
 */
public class Data {
    private List<Coordinate> coordinates;
    private Cart cart;

    /**
     * used for deserialization
     */
    private Data(){

    }

    /**
     * to set data
     * @param coordinates list of Coordinates
     * @param cart cart
     */
    public Data(List<Coordinate> coordinates, Cart cart){
        this.coordinates = coordinates;
        this.cart = cart;
    }

    /**
     *
     * @return coordinates
     */
    public List<Coordinate> getCoordinates() {
        return coordinates;
    }

    /**
     *
     * @return cart
     */
    public Cart getCart() {
        return cart;
    }

    @Override
    public String toString() {
        return "Data{" +
                "coordinates=" + coordinates +
                ", cart=" + cart +
                '}';
    }
}
