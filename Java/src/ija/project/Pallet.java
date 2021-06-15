package ija.project;

/**
 * Data of one pallet in storage,
 * We have to know item and its count
 */
public class Pallet {
    private Item item;
    private int numOfItems;

    /**
     *
     * @param item - which item is added
     * @param numOfItems - amount of added item
     */
    public Pallet(Item item, int numOfItems) {
        this.item = item;
        this.numOfItems = numOfItems;
    }

    /**
     * used for deserialization
     */
    public Pallet() { }

    /**
     *
     * @return object item wih all the necessary information
     */
    public Item getItem() {
        return item;
    }

    /**
     *
     * @param item Item which is added to the pallet
     */
    public void setItem(Item item) {
        this.item = item;
    }

    /**
     *
     * @return int representing amount of items in pallet
     */
    public int getNumOfItems() {
        return numOfItems;
    }

    /**
     * sets number of items
     * @param numOfItems int sets
     */
    public void setNumOfItems(int numOfItems) {
        this.numOfItems = numOfItems;
    }
}
