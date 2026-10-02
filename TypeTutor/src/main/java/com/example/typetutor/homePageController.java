package com.example.typetutor;

import javafx.fxml.FXML;
import javafx.scene.Node;
import javafx.scene.control.Label;
import javafx.event.ActionEvent;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.TextField;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.scene.text.TextFlow;
import javafx.stage.Stage;

import java.io.IOException;
import java.net.Socket;
import java.util.Objects;
import com.example.typetutor.WaitingRoomController;

public class homePageController {

    public void goToSoloScene(ActionEvent event){
         try {
             SoloController.indexSetter();
             Parent root = FXMLLoader.load(getClass().getResource("Solo.fxml"));
             Stage stage = (Stage) ((javafx.scene.Node) event.getSource()).getScene().getWindow();
             stage.setScene(new Scene(root));

         } catch (IOException e) {
             throw new RuntimeException(e);
         }
     }

     public void exiting(ActionEvent event) throws IOException {
         System.exit(0);
     }

public void goToMultiplayerScene(ActionEvent event) {
    try {
        // Connect to server
        Socket socket = new Socket("192.168.0.103", 5050);
        SocketWrapper wrapper = new SocketWrapper(socket);
        WaitingRoomController.setSocketWrapper(wrapper);

        // Load FXML and controller
        FXMLLoader loader = new FXMLLoader(getClass().getResource("WaitingRoom.fxml"));
        Parent root = loader.load();

        WaitingRoomController controller = loader.getController();

        // Get current stage from event
        Stage currentStage = (Stage) ((Node) event.getSource()).getScene().getWindow();

        // Pass stage and start timeline
        controller.setStage(currentStage);
        controller.startCheckingClients();

        // Show scene
        currentStage.setScene(new Scene(root));
        currentStage.show();

    } catch (IOException e) {
        throw new RuntimeException(e);
    }
}

    public void goToColorBlindScene(ActionEvent event){
        try {
            SoloController.indexSetter();
            Parent root = FXMLLoader.load(getClass().getResource("ColorBlind.fxml"));
            Stage stage = (Stage) ((javafx.scene.Node) event.getSource()).getScene().getWindow();
            stage.setScene(new Scene(root));

        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

public void goToRecordScene(ActionEvent event) throws IOException {
    Parent root = FXMLLoader.load(getClass().getResource("Record.fxml"));
    Stage stage = (Stage) ((javafx.scene.Node) event.getSource()).getScene().getWindow();
    stage.setScene(new Scene(root));
}
}