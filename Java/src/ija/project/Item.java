package ija.project;

/**
 * Data of one item in shelf,
 * We have to know only weight and ID of item
 */
public class Item {
    private String ID;
    private double weight;

    /**
     * initialize Item
     */
    public Item() {
    }

    /**
     * set values to Item
     * @param ID - sting ID - unique item
     * @param weight - double representing weight of item
     */
    public Item(String ID, double weight) {
        this.weight = weight;
        this.ID = ID;
    }

    /**
     * to return weight of item
     * @return - double weight
     */
    public double getWeight() {
        return weight;
    }

    /**
     * to return name of item
     * @return - string ID
     */
    public String getID() {
        return ID;
    }

    /**
     * to set weight of an item
     * @param weight double weight of item
     */
    public void setWeight(double weight) {
        this.weight = weight;
    }

    /**
     * to set name for item
     * @param ID string passed to items ID
     */
    public void setID(String ID) {
        this.ID = ID;
    }
}
