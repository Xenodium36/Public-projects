package ija.project;

import com.fasterxml.jackson.databind.annotation.JsonDeserialize;

import java.util.List;

/**
 * Defining shelf
 * Shelf contains: Coordinates, where its located
 *                 Item
 *                 Number if items
 */
@JsonDeserialize(as = Shelf.class)
public class Shelf {
    private Coordinate place;
    private List<Pallet> pallets;

    public Shelf() {
    }

    public Shelf(Coordinate place, List<Pallet> pallets) {
        this.place = place;
        this.pallets = pallets;
    }

    public List<Pallet> getPallets() {
        return pallets;
    }

    public Double getWeightByName(String name){
        for (Pallet pallet : pallets){
            if(pallet.getItem().getID().equals(name)){
                return pallet.getItem().getWeight();
            }
        }
        return null;
    }

    public void setPallets(List<Pallet> pallets) {
        this.pallets = pallets;
    }

    public Coordinate getPlace() {
        return place;
    }

    public void setPlace(Coordinate place) {
        this.place = place;
    }

    public void setNumOfItemsByName(String name, int newNum){
        for (Pallet pallet : pallets){
            if(pallet.getItem().getID().equals(name)){
                pallet.setNumOfItems(newNum);
            }
        }
    }
    public int getNumOfItemsByName(String name){
        for (Pallet pallet : pallets){
            if(pallet.getItem().getID().equals(name)){
                return pallet.getNumOfItems();
            }
        }
        return 0;
    }
}
