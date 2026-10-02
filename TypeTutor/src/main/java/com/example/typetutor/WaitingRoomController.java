
package com.example.typetutor;
import com.example.typetutor.SocketWrapper;
import javafx.animation.Animation;
import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Platform;
import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Node;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Label;
import javafx.scene.control.Slider;
import javafx.scene.control.TextField;
import javafx.scene.layout.AnchorPane;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.scene.text.TextFlow;
import javafx.stage.Stage;
import javafx.util.Duration;

import javax.swing.*;
import java.io.IOException;
import java.util.Random;


public class WaitingRoomController {

    @FXML
    private AnchorPane rootbox; // Or whatever you used in FXML
    private Timeline timeline;

    private static SocketWrapper socketWrapper;
    private Stage stage;

    public static void setSocketWrapper(SocketWrapper wrapper) {
        socketWrapper = wrapper;
    }

    public void setStage(Stage stage) {
        this.stage = stage;
    }

    public void startCheckingClients() {
        // Timeline runs repeatedly every 2 second to check condition
        timeline = new Timeline(
                new KeyFrame(Duration.seconds(0.1), event -> checkClientCount())
        );
        timeline.setCycleCount(Timeline.INDEFINITE);
        timeline.play();
    }

    private void checkClientCount() {
        try {
            socketWrapper.write("PARAGRAPH NO.");
            idx=(Integer) socketWrapper.read();
            socketWrapper.write("GET_CLIENT_COUNT");
            String reply = (String) socketWrapper.read();
            //   System.out.println(reply);

              if (reply.startsWith("CLIENT_COUNT:")) {

                  int count = Integer.parseInt(reply.split(":")[1]);
                //      System.out.println("Clients: " + count);
                  if (count == 2) {
                 Platform.runLater(this::switchToGameScene); // Always use Platform.runLater for UI change
                 // Platform.runLater(() -> switchToGameScene()); // “I’m in a background thread. I want the UI to change. So I’ll tell JavaFX: ‘Hey, when you’re back on the UI thread, please run this code.’”
                }
        }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // Multiplayer type racer scene start from here!!!

    @FXML
    private Label WPM;
    private String[] s=
            {
                    "Quantum mechanics is the branch of physics that deals with the behavior of particles at the atomic and subatomic scale. It introduces concepts such as wave-particle duality, superposition, and entanglement, which defy classical intuition. Unlike classical mechanics, quantum theory suggests that the act of observation affects the system being observed.",
                    "Lionel Messi, the little boy from Rosario, stands atop the world finally, eternally. He has danced through the ages, a symphony of left-footed genius, and now, at last, the golden trophy is his. The World Cup, long elusive, rests in the hands of the man who made the beautiful game more beautiful. Argentina weeps, the world applauds, and football glorious, magical football bows at the feet of its humble king.",
            };

    @FXML
    private TextField textField = new TextField();
    @FXML
    private TextFlow textFlow = new TextFlow();
    private boolean start = true;
    private long startTime;
    private long endTime;
    private int wpm; // Word Per Minite
    private static int idx;
    @FXML
    private Slider slider1 = new Slider();
    @FXML
    private Slider slider2 = new Slider();
    @FXML
    private Label WPM2= new Label();
    @FXML
    private Label ACCURACY1= new Label();
    @FXML
    private Label ACCURACY2= new Label();
    private float accuracy1;
    private float accuracy2;
    private float accuracyPerletter;


@FXML
private void switchToGameScene() {
    try {
        if (timeline != null) {
            timeline.stop();
        }

        FXMLLoader loader = new FXMLLoader(getClass().getResource("Multiplayer.fxml"));
        Parent root = loader.load();

        // ✅ Set up the controller
        WaitingRoomController controller = loader.getController();
        controller.prepareGame(); // Custom method to setup textflow and listener
        stage.setScene(new Scene(root));

    } catch (IOException e) {
        e.printStackTrace();
    }
}
  @FXML
    public void prepareGame() {
        slider1.setMin(0);
        slider1.setMax(s[idx].length());
        slider1.setValue(0); // Start from zero
        slider2.setMin(0);
        slider2.setMax(s[idx].length());
        slider2.setValue(0);
//      slider1.getStyleClass().add("blue-slider");
//      slider2.getStyleClass().add("red-slider");
        accuracyPerletter = 100.0F/s[idx].length();
        accuracy1 = 100.0F;
        accuracy2 = 100.0F;
       // ACCURACY1.setText("Accuracy : "+ String.valueOf(accuracy1)+"%");
      // ACCURACY2.setText("Accuracy : "+ String.valueOf(accuracy2)+"%");


        updateTextFlow("");  // Load paragraph
        startTime = System.currentTimeMillis();

        // Background thread to receive opponent's progress from server
        new Thread(() -> {
            try {
                while (true) {
                    String msg = (String) socketWrapper.read(); // Blocking call
                    if (msg.startsWith("OPPONENT_PROGRESS:")) {
                        int progress = Integer.parseInt(msg.split(":")[1]);
                        System.out.println("OPPONENT_PROGRESS: " + progress + " to " + Server.clientMap.get(socketWrapper));
                        //Platform.runLater(() -> slider2.setValue(progress));
                        Platform.runLater(() -> {
                            slider2.setValue(progress);
                        });
                        //    JavaFX is single-threaded for UI updates, meaning:
                        //  You can only modify UI components (like sliders, labels, buttons, etc.) from the JavaFX Application Thread.
                        //   If you're in a background thread (like reading from a socket), and you try to update the UI directly, it will crash or throw an exception.
                    }
                    else if (msg.startsWith("OPPONENT_WPM:")) {
                        int wpm2=Integer.parseInt(msg.split(":")[1]);
                        System.out.println("OPPONENT_WPM: " + wpm2);
                        Platform.runLater(() -> {WPM2.setText("WPM: " + wpm2);});
                    }
                    else if (msg.startsWith("OPPONENT_ACCURACY:")) {
                        float accuracy=Float.parseFloat(msg.split(":")[1]);
                        System.out.println("OPPONENT_ACCURACY: " + accuracy);
                        Platform.runLater(() -> {ACCURACY2.setText(String.format("Opponent Accuracy : %.2f%%", accuracy));});
                    }
                }
            } catch (IOException | ClassNotFoundException e) {
                e.printStackTrace();
            }
        }).start();

        textField.textProperty().addListener((observable, oldValue, newValue) -> {
            if (newValue.length() >= s[idx].length()) {
                textField.setEditable(false);
                endTime = System.currentTimeMillis();

                long durationMillis = endTime - startTime;
                double durationMinutes = durationMillis / 60000.0;
                int totalWords = s[idx].length() / 5;
                int wpm = (int) (totalWords / durationMinutes);
                WPM.setText("WPM : " + wpm);
                ACCURACY1.setText(String.format("Your Accuracy : %.2f%%", accuracy1));
                try {
                    socketWrapper.write("WPM:"+wpm);
                    socketWrapper.write("Accuracy:"+accuracy1);
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            }
            slider1.setValue(newValue.length());
            try {
                socketWrapper.write("Progress:"+newValue.length());

            } catch (IOException e) {
                throw new RuntimeException(e);
            }
            updateTextFlow(newValue);
        });
      Platform.runLater(() -> textField.requestFocus());
    }


    private void updateTextFlow(String userInput) {
        textFlow.getChildren().clear();
        int mistake=0;
        for (int i = 0; i < s[idx].length(); i++) {
            Text t = new Text(String.valueOf(s[idx].charAt(i)));  // Text t = new Text(s1.charAt(i)); -> wrong
            t.setStyle("-fx-font-size: 20px;");               // The reason is: Text constructor expects a String, not a char.
            if (i < userInput.length()) {
                if (userInput.charAt(i) == s[idx].charAt(i)) {
                    t.setFill(Color.GREEN);
                } else {
                    t.setFill(Color.RED);
                    mistake++;
                }
            } else {
                t.setFill(Color.BLACK);
            }

            textFlow.getChildren().add(t);
        }
        accuracy1 = 100.0F - (mistake*accuracyPerletter);
    }

    @FXML
    public void goBackHome(ActionEvent event) throws IOException {
        Stage stage = (Stage)((Node) event.getSource()).getScene().getWindow();
        stage.setScene(MainHomePage.homeScene);
     //   Server.clientMap.remove(socketWrapper);
        socketWrapper.write("DISCONNECT");
     //   Random rand = new Random();
       // idx= rand.nextInt(2);
    }
}

