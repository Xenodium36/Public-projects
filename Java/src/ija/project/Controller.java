package ija.project;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.type.CollectionType;
import com.fasterxml.jackson.dataformat.yaml.YAMLFactory;
import com.fasterxml.jackson.dataformat.yaml.YAMLGenerator;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.scene.control.*;
import javafx.scene.input.MouseEvent;
import javafx.scene.input.ScrollEvent;
import javafx.scene.layout.Pane;

import javafx.scene.paint.Color;
import javafx.scene.shape.Circle;
import javafx.scene.shape.Line;
import javafx.scene.shape.Shape;
import javafx.util.Pair;
import org.jgrapht.alg.shortestpath.DijkstraShortestPath;
import org.jgrapht.graph.DefaultWeightedEdge;

import java.io.File;
import java.time.LocalTime;
import java.util.*;

import static ija.project.ShelfData.getDistance;

/**
 * Controls, what is happening at javafx application
 */
public class Controller {
    ////////////////////////////////////////////////////////////////////////////////

    @FXML
    public Pane content;

    /// Animation speed

    @FXML
    private TextField timeScale;
    private float scale = 1;
    private Timer timer;
    private LocalTime time = LocalTime.now();
    @FXML
    public ToggleButton toggleStopStart;

    /// Default scenario

    public ComboBox<Object> dropDefLayout;
    @FXML
    private ToggleButton ToggleScenarioDef;
    public ComboBox<Object> dropOrderList;

    /// Custom scenario

    public ComboBox<Object> dropCustLayout;
    @FXML
    private ToggleButton ToggleScenarioCust;
    public ComboBox<String> dropSelectItem;
    @FXML
    private TextField TextFieldAmount;

    /// overview
    public TextArea textAreaOverview;

    /// additional actions
    public ComboBox<Object> dropLayout;

    /// bottom fields
    public Label labelBott;
    public TextArea textAreaDetails;

    ///////////////////////

    private Map<String, Integer> orderItemsMap = new HashMap<>();
    private List<WantedData> customWantedData = new ArrayList<>();


    private List<Circle> blockCircles = new ArrayList<>();
    public List<Line> cartPathLines = new ArrayList<>();
    private List<Drawable> elements = new ArrayList<>();
    private LocalTime timeOfDrawingPath;


    private List<TimeUpdate> updates = new ArrayList<>();
    private ShelfData shelfData = new ShelfData();

    private DijkstraShortestPath<Coordinate, DefaultWeightedEdge> dSPath;


    private Graph graph = new Graph();
    private ObjectMapper mapper;

    /// FUNCTIONS //////////////////////////////////////////////////////////////

    /**
     * controller initialization
     *     - set new mapper
     *     - create graph
     *     - set shortest path
     */
    public void initializeController(){
        YAMLFactory factory = new YAMLFactory().disable(YAMLGenerator.Feature.WRITE_DOC_START_MARKER);
        mapper = new ObjectMapper(factory);
        graph.createGraph();
        dSPath = new DijkstraShortestPath<>(graph.getGraph());
    }

    /**
     * Changing speed of inner clock of the application
     */
    @FXML
    private void onTimeScaleChange(){
        try {
            scale = Float.parseFloat(timeScale.getText());
            if (scale < 0 || scale > 4.0){
                Alert alert = new Alert(Alert.AlertType.ERROR, "Invalid time scale");
                alert.showAndWait();
                return;
            }
            timer.cancel();
            startTime(scale);
        } catch (NumberFormatException e) {
            Alert alert = new Alert(Alert.AlertType.ERROR, "Invalid time scale");
            alert.showAndWait();
            timeScale.setText("");
        }
    }

    /**
     * function to refresh pane with added cart path line
     */
    public void refreshPane(){
        for(Line line : cartPathLines){
            content.getChildren().add(line);
        }
        timeOfDrawingPath = LocalTime.now();

    }

    /**
     * Zoom in and out using scaling
     * MAX scale is 3, MIN scale is 0.2
     * @param event Received scrolling event
     */
    @FXML
    private void onZoom(ScrollEvent event){
        event.consume();
        double zoom = event.getDeltaY() > 0 ? 1.1 : 0.9;
        if (zoom * content.getScaleX() > 0.2 && zoom * content.getScaleX() < 3){
            content.setScaleX(zoom * content.getScaleX());
            content.setScaleY(zoom * content.getScaleY());
            content.layout();
        }
    }

    /**
     *
     * @param elements Array of Drawable from Main, it contains every cart and update, we want to draw
     */
    public void setElements(List<Drawable> elements) {
        this.elements = elements;
        for (Drawable drawable : elements){
            content.getChildren().addAll(drawable.getGUI());
            if(drawable instanceof TimeUpdate){
                updates.add((TimeUpdate) drawable);
            }
        }
    }

    /**
     * Starts inner clock of program, user can change speed of it
     * @param scale Scale of time, default 1
     */
    public void startTime(double scale){
        timer = new Timer(false);
        timer.scheduleAtFixedRate(new TimerTask() {
            @Override
            public void run() {
                time = time.plusSeconds(1);
                for (TimeUpdate update : updates){
                    update.update(time);
                }
            }
        }, 0, (long)(1000 / scale));

    }

    /**
     * This function writes to GUI, what shelf contains, when user click at that shelf,
     * blocks stop for new deployd carts and removes carts path line
     * @param mouseEvent Event of click on Pane
     */
    public void paneClick(MouseEvent mouseEvent) {

        Coordinate coordinate = new Coordinate(mouseEvent.getX(), mouseEvent.getY());

        // remove carts path line
        if(timeOfDrawingPath != null && timeOfDrawingPath.plusSeconds((long) (2.5 * scale)).isBefore(time)){
            for (Line line : cartPathLines){
                content.getChildren().remove(line);
            }
        }

        // shelfData display
        try {
            Shelf shelf = shelfData.getShelfByCoords(coordinate);
            String tmp = shelfData.shelfItemsToString(shelf);
            labelBott.setText(tmp);
            return;
        }
        catch (NullPointerException e){
            labelBott.setText("");
        }

        // stop block handling
        Coordinate circleOnCoords = Graph.getStopByCoords(coordinate);

        if (circleOnCoords == null)
            return;

        if(!circleOnCoords.isEnabled()){

            for(Circle circle : blockCircles){
                if (circleOnCoords.checkIfEquals(new Coordinate(circle.getCenterX(), circle.getCenterY()))){
                    content.getChildren().remove(circle);
                    this.blockCircles.remove(circle);
                    break;
                }
            }
            circleOnCoords.setEnabled(true);
            System.out.println(circleOnCoords.toString()+"  is now enabled"+ blockCircles.size());
        }else{
            Circle circle = new Circle(circleOnCoords.getX(), circleOnCoords.getY(),5,Color.RED);
            this.blockCircles.add(circle);
            circleOnCoords.setEnabled(false);
            content.getChildren().add(circle);
        }
        graph.createGraph();
        dSPath = new DijkstraShortestPath<>(graph.getGraph());
    }

    /**
     *
     * @param actionEvent - stop or start carts
     */
    public void timeToggle(ActionEvent actionEvent) {
        if (toggleStopStart.isSelected()){
            timer.cancel();
            startTime(0);
        }else {
            timer.cancel();
            startTime(scale);
        }
    }

    /**
     * load chosen layout form file in data directory
     */
    public void loadLayout(){

        if (dropLayout.getValue() == null){
            labelBott.setText("Layout not selected.");
            return;
        }

        CollectionType javaType = mapper.getTypeFactory().constructCollectionType(List.class, Shelf.class);
        try {
            shelfData.setShelves(mapper.readValue(new File("data/" + dropLayout.getValue() + ".yml"), javaType));
        }
        catch (Exception e){
            labelBott.setText("Error! File "+ dropLayout.getValue() +" doesn't exist.");
        }
    }

    /**
     * for loading empty layout with items of 0 weight and 0 count
     */
    public void loadEmptyLayout(){
        CollectionType javaType = mapper.getTypeFactory().constructCollectionType(List.class, Shelf.class);
        try {
            shelfData.setShelves(mapper.readValue(new File("data/EMPTY.yml"), javaType));
        }
        catch (Exception e){
            labelBott.setText("Error! File data/EMPTY.yml doesn't exist.");
        }
    }

    /**
     *
     * @param type - 1 default scenario; 2 custom scenario
     */
    private void playScenario(int type){

        // default scenario
        if (type == 1){
            if (!ToggleScenarioDef.isSelected()){
                CollectionType javaType = mapper.getTypeFactory().constructCollectionType(List.class, Shelf.class);
                try {
                    shelfData.setShelves(mapper.readValue(new File("data/" + dropDefLayout.getValue() + ".yml"), javaType));
                }
                catch (Exception e){
                    labelBott.setText("Error! File "+ dropDefLayout.getValue() +" doesn't exist.");
                    return;
                }
            }

            CollectionType javaTypeWanted = mapper.getTypeFactory().constructCollectionType(List.class, WantedData.class);
            try{
                customWantedData = mapper.readValue(new File("data/"+ dropOrderList.getValue() +".yml"), javaTypeWanted);
            }
            catch (Exception e){

                labelBott.setText("Error! File "+ dropOrderList.getValue() +" doesn't exist.");
                return;
            }

        // custom scenario
        } else {
            if (!ToggleScenarioCust.isSelected()) {
                CollectionType javaType = mapper.getTypeFactory().constructCollectionType(List.class, Shelf.class);
                try {
                    shelfData.setShelves(mapper.readValue(new File("data/" + dropCustLayout.getValue() + ".yml"), javaType));
                } catch (Exception e) {
                    labelBott.setText("Error! File " + dropCustLayout.getValue() + " doesn't exist.");
                    return;
                }
            }
        }


        if (shelfData.getShelves() == null){
            labelBott.setText("Error! Could not read file: " + dropCustLayout.getValue());
            return;
        }

        List<Pair<WantedData, Shelf>> map = new ArrayList<>();
        map = createMapForCart(customWantedData, map, graph.getStart());

        if (map == null){
            labelBott.setText("No items found");
        }else{
            List<List<Pair<WantedData, Shelf>>> mapList = checkMaxWeight(map, new ArrayList<>());
            for (List<Pair<WantedData, Shelf>> tmpMap : mapList){
                Path path = getPathForCart(tmpMap, graph.getStart());
                if(path != null){
                    Cart cart = new Cart(graph.getStart(), 20, path, getStops(tmpMap), this);
                    List<Drawable> elTmp = new ArrayList<>();
                    elTmp.add(cart);
                    setElements(elTmp);
                }
            }
        }

    }

    /**
     * This function checks default scenario after hitting PLAY button in concerned section in GUI
     */
    public void playDefaultScenario() {
        if (dropDefLayout.getValue() == null){
            labelBott.setText("layout not set.");
            return;
        }

        if (dropOrderList.getValue() == null){
            labelBott.setText("test order not set.");
            return;
        }
        playScenario(1);
    }

    /**
     * This function checks overview list of items and layout upon hitting PLAY button in concerned section in GUI
     */
    public void playCustomScenario() {
        mapToWantedList(orderItemsMap);
        playScenario(2);
    }

    /**
     * removes item or its amount from custom order
     */
    public void removeItem() {
        String amountStr = TextFieldAmount.getText();
        String itemName = dropSelectItem.getValue();
        int amountInt;

        try {
            amountInt = Integer.parseInt(amountStr);
        } catch (NumberFormatException e){
            labelBott.setText("Error! \"" + amountStr + "\" is not a valid number.");
            TextFieldAmount.setText("");
            return;
        }
        if (itemName == null){
            textAreaOverview.setText("No selected item.");
        }

        if (amountInt < 0) {
            labelBott.setText("Error! negative number is not a valid.");
            TextFieldAmount.setText("");
            return;
        }

        Integer count = orderItemsMap.get(itemName);
        count = count == null ? amountInt : count - amountInt;

        if (count > 0){
            orderItemsMap.put(itemName, count);
            updateOverviewTextArea();
            return;
        }

        orderItemsMap.remove(itemName);
        updateOverviewTextArea();
    }

    /**
     *  adds item or to its amount to custom order
     */
    public void addItem() {
        String amountStr = TextFieldAmount.getText();
        String itemName = dropSelectItem.getValue();
        int amountInt;

        try {
            amountInt = Integer.parseInt(amountStr);
        } catch (NumberFormatException e){
            labelBott.setText("Error! \"" + amountStr + "\" is not a valid number.");
            TextFieldAmount.setText("");
            return;
        }
        if (itemName == null){
            textAreaOverview.setText("No selected item.");
        }

        if (amountInt < 0) {
            labelBott.setText("Error! negative number is not a valid.");
            TextFieldAmount.setText("");
            return;
        }

        Integer count = orderItemsMap.get(itemName);
        count = count == null ? amountInt : count + amountInt;

        orderItemsMap.put(itemName, count);
        updateOverviewTextArea();
    }

    /**
     *  redisplay correct custom order
     */
    public void updateOverviewTextArea() {
        List<String> orderedItems = new ArrayList<>(orderItemsMap.keySet());
        Collections.sort(orderedItems);
        String text = "";

        for (String item : orderedItems) {
            text += item + ": " + orderItemsMap.get(item) + "\n";
        }

        textAreaOverview.setText(text);
    }

    /**
     *  clear custom order and clear overview
     */
    public void clearOverview(){
        orderItemsMap.clear();
        updateOverviewTextArea();
    }

    /**
     *
     * @param map passed map sets values for customWantedList
     */
    private void mapToWantedList(Map<String, Integer> map){
        for (String key : map.keySet()) {
            WantedData wd = new WantedData(key, map.get(key));
            customWantedData.add(wd);
        }
    }

    /**todo
     *Function to get every stop at the path of the cart
     * @param map map of places, where is cart going
     * @return
     */
    private List<Coordinate> getStops(List<Pair<WantedData, Shelf>> map){
        List<Coordinate> tmpList= new ArrayList<>();
        for(Pair<WantedData, Shelf> pair : map){
            if (tmpList.size() == 0) {
                tmpList.add(pair.getValue().getPlace());
            }
            else if (!pair.getValue().getPlace().checkIfEquals(tmpList.get(tmpList.size()-1))){
                tmpList.add(pair.getValue().getPlace());
            }
        }
        tmpList.add(new Coordinate(100, 260));
        return tmpList;
    }

    /**
     * Recursive function to create map for cart
	 * Finding the "optimal" path for cart
	 * Could be better, not enought time
     * @param wanted which item are needed from storage
     * @param map map of every place, which needs to be visited
     * @param coordinate actual coordinate
     * @return map for the cart
     */
    private List<Pair<WantedData, Shelf>> createMapForCart(List<WantedData> wanted, List<Pair<WantedData, Shelf>> map, Coordinate coordinate){
        SortedMap<Double, Pair<WantedData, Shelf>> tmpMap = new TreeMap<>();
        WantedData tmpNotFound = new WantedData();
        for (WantedData wantedData : wanted){
            Shelf tmpShelf = shelfData.getClosestShelfEnough(coordinate, wantedData.getName(), wantedData.getNumOfItems());
            if(tmpShelf != null){
                Pair<WantedData, Shelf> tmp = new Pair<>(wantedData, tmpShelf);
                double dist = getDistance(coordinate, tmpShelf.getPlace());
                tmpMap.put(dist, tmp);
            }else{
                List<Shelf> more = shelfData.getShelvesNotEnough(wantedData.getName(), wantedData.getNumOfItems());
                if (more == null){
                    tmpNotFound = wantedData;
                    labelBott.setText(wantedData.getName() + ": not enough of this item in storage or item does not exist");
                }else{
                    for (Shelf shelf : more) {
                        Pair<WantedData, Shelf> tmp = new Pair<>(wantedData, shelf);
                        double dist = getDistance(coordinate, shelf.getPlace());
                        tmpMap.put(dist, tmp);
                    }
                }
            }
        }
        if (tmpMap.size() == 0){
            return null;
        }
        int newNumOfItems = tmpMap.get(tmpMap.firstKey()).getValue().getNumOfItemsByName(tmpMap.get(tmpMap.firstKey()).getKey().getName()) - tmpMap.get(tmpMap.firstKey()).getKey().getNumOfItems();
        if(newNumOfItems < 0) newNumOfItems = 0;
        coordinate = tmpMap.get(tmpMap.firstKey()).getValue().getPlace();
        for (int i = 0; i < wanted.size(); i++){
            if(wanted.get(i).getName().equals(tmpNotFound.getName())){
                wanted.remove(i);
            }
            if (wanted.get(i).getName().equals(tmpMap.get(tmpMap.firstKey()).getKey().getName())){
                if(wanted.get(i).getNumOfItems() - tmpMap.get(tmpMap.firstKey()).getValue().getNumOfItemsByName(wanted.get(i).getName()) <= 0) {
                    map.add(new Pair<>(wanted.get(i), tmpMap.get(tmpMap.firstKey()).getValue()));
                    wanted.remove(i);
                }else {
                    WantedData tmpWanted = new WantedData(wanted.get(i).getName(), tmpMap.get(tmpMap.firstKey()).getValue().getNumOfItemsByName(tmpMap.get(tmpMap.firstKey()).getKey().getName()));
                    map.add(new Pair<>(tmpWanted, tmpMap.get(tmpMap.firstKey()).getValue()));
                    wanted.get(i).setNumOfItems(wanted.get(i).getNumOfItems() - tmpMap.get(tmpMap.firstKey()).getValue().getNumOfItemsByName(wanted.get(i).getName()));
                }
                break;
            }
        }
        shelfData.getShelfByCoords(tmpMap.get(tmpMap.firstKey()).getValue().getPlace()).setNumOfItemsByName(tmpMap.get(tmpMap.firstKey()).getKey().getName(), newNumOfItems);
        if (wanted.size() != 0){
            createMapForCart(wanted, map, coordinate);
        }
        return map;
    }

    /**
     * Checking, if 1 cart can take every item at map. 
	 *If not, it creates List of maps for more carts
     * @param map
     * @param tmpMapList
     * @return List of maps for more carts
     */
    private List<List<Pair<WantedData, Shelf>>> checkMaxWeight(List<Pair<WantedData, Shelf>> map, List<List<Pair<WantedData, Shelf>>> tmpMapList){
        List<Pair<WantedData, Shelf>> tmpMap = new ArrayList<>();
        List<Pair<WantedData, Shelf>> newMap = new ArrayList<>();
        double maxCartWeight = 100;
        double actualWeight = 0;
        for(Pair<WantedData, Shelf> pair : map){
            if(actualWeight + pair.getKey().getNumOfItems() * pair.getValue().getWeightByName(pair.getKey().getName()) > maxCartWeight){
                int i = pair.getKey().getNumOfItems();
                while (actualWeight + i * pair.getValue().getWeightByName(pair.getKey().getName()) >= maxCartWeight){
                    i--;
                }
                if (i > 0){
                    actualWeight = actualWeight + i * pair.getValue().getWeightByName(pair.getKey().getName());
                    tmpMap.add(new Pair<>(new WantedData(pair.getKey().getName(), i), pair.getValue()));
                    newMap.add(new Pair<>(new WantedData(pair.getKey().getName(), pair.getKey().getNumOfItems() - i), pair.getValue()));
                }else {
                    newMap.add(new Pair<>(new WantedData(pair.getKey().getName(), pair.getKey().getNumOfItems()), pair.getValue()));
                }

            }else {
                tmpMap.add(pair);
                actualWeight = actualWeight + pair.getKey().getNumOfItems() * pair.getValue().getWeightByName(pair.getKey().getName());
            }
        }
        tmpMapList.add(tmpMap);
        if(newMap.size() != 0){
            checkMaxWeight(newMap, tmpMapList);
        }
        return tmpMapList;
    }

    /**
     * Findes shotrest path throught graph using Dijkstra algorithm
     * @param map map for just one cart
     * @param coordinate actual coordinate
     * @return path for cart
     */
    private Path getPathForCart(List<Pair<WantedData, Shelf>> map, Coordinate coordinate){
        Path path = new Path();
        Path p1 = new Path();
        Path p2 = new Path();
        double sizeP1;
        double sizeP2;
        Coordinate end = new Coordinate(100, 260);

        for(Pair<WantedData, Shelf> pair : map){
            sizeP1 = Integer.MAX_VALUE;
            sizeP2 = Integer.MAX_VALUE;
            try{
                p1.setPath(dSPath.getPath(coordinate, new Coordinate(pair.getValue().getPlace().getX() + 40, pair.getValue().getPlace().getY())).getVertexList());
                sizeP1 = p1.getPathSize();
            }catch (NullPointerException ignored){}
            try{
                p2.setPath(dSPath.getPath(coordinate, new Coordinate(pair.getValue().getPlace().getX() - 40, pair.getValue().getPlace().getY())).getVertexList());
                sizeP2 = p2.getPathSize();
            }catch (NullPointerException ignored){}
            if(path.getPath().size() > 0 && ((sizeP2 > 0 && path.getPath().get(path.getPath().size() - 1).checkIfEquals(p2.getPath().get(0)))
                    || (sizeP1 > 0 && path.getPath().get(path.getPath().size() - 1).checkIfEquals(p1.getPath().get(0))))){
                path.getPath().remove(path.getPath().size() - 1);
            }
            if(sizeP1 > sizeP2){
                path.addToPath(p2.getPath());
                coordinate = new Coordinate(pair.getValue().getPlace().getX() - 40, pair.getValue().getPlace().getY());

            }else if (sizeP1 < sizeP2){
                path.addToPath(p1.getPath());
                coordinate = new Coordinate(pair.getValue().getPlace().getX() + 40, pair.getValue().getPlace().getY());
            }
            if (sizeP1 == Integer.MAX_VALUE && sizeP2 == Integer.MAX_VALUE){
                labelBott.setText("Cant get to shelf at coordinates x = " + pair.getValue().getPlace().getX() + ", y = "
                        + pair.getValue().getPlace().getY() + "\n to get item " + pair.getKey().getName());
            }
        }
        if(path.getPathSize() == 0){
            return null;
        }else{
            path.getPath().remove(path.getPath().size() - 1);
            path.addToPath(dSPath.getPath(coordinate, end).getVertexList());
            Coordinate BackLeft = new Coordinate(100, 530);
            Coordinate BackRight = new Coordinate(660, 530);
            List<Coordinate> finish = new ArrayList<Coordinate>();
            finish.add(BackLeft);
            finish.add(BackRight);
            finish.add(graph.getStart());
            path.addToPath(finish);
            return path;
        }
    }

}