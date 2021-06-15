package ija.project;

import javafx.application.Application;
import javafx.application.Platform;
import javafx.fxml.FXMLLoader;
import javafx.scene.Scene;
import javafx.scene.layout.BorderPane;
import javafx.stage.Stage;

/**
 * Just a normal main
 */
public class Main extends Application {

    /**
     * Creates and sets primary stage
     * Then YAMFactory is created, so we can get data from .yml files
     * Then we set that red data to Array elements, so we can draw it
     * If it gets request, that GUI was closed by user, the program ends
     * @param primaryStage Its used to work with GUI
     *
     */
    @Override
    public void start(Stage primaryStage) throws Exception{
        FXMLLoader loader = new FXMLLoader(getClass().getClassLoader().getResource("layout.fxml"));
        primaryStage.setTitle("Storage");

        BorderPane root = loader.load();
        Scene scene = new Scene(root);
        primaryStage.setScene(scene);
        primaryStage.show();
        Controller controller = loader.getController();

        controller.initializeController();
        controller.startTime(1);

        primaryStage.setOnCloseRequest(windowEvent -> {
            Platform.exit();
            System.exit(0);
        });
    }

    public static void main(String[] args) {
        launch(args);
    }

}
