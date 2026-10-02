package com.example.typetutor;

import javafx.animation.KeyFrame;
import javafx.animation.Timeline;
import javafx.application.Platform;
import javafx.fxml.FXML;
import javafx.scene.Node;
import javafx.scene.control.Label;
import javafx.event.ActionEvent;
import javafx.fxml.FXMLLoader;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.control.Slider;
import javafx.stage.Stage;

import javafx.geometry.Insets;
import javafx.scene.control.TextField;
import javafx.scene.layout.VBox;
import javafx.scene.paint.Color;
import javafx.scene.text.Text;
import javafx.scene.text.TextFlow;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.Objects;
import javafx.scene.control.Button;
import javafx.util.Duration;

import javax.swing.*;
import java.util.Random;
import java.util.Scanner;

public class ColorBlindController {
    @FXML
    private Label WPM;
    private String[] s=
            {
                    "Robert the Bruce, the legendary King of Scots, was a symbol of perseverance and courage. After facing several defeats in battle, he found inspiration in a spider tirelessly spinning its web. Each time the spider fell, it climbed back and tried again—until it succeeded. This simple act renewed Bruce’s determination, and he eventually led Scotland to victory at the Battle of Bannockburn in 1314. His story teaches us to never give up, no matter how many times we fail.",
                    "Alexander Hamilton was born in poverty but rose to power through the strength of his writing. A letter he wrote as a teen about a storm amazed the local people, who raised funds for him to study in New York. He went on to help write the Constitution and lead the Treasury. Hamilton's life proves that words have the power to transform your future."
            };

    @FXML
    private TextField textField = new TextField();
    @FXML
    private TextFlow textFlow = new TextFlow();
    private boolean start = true;
    private long startTime;
    private long endTime;
    @FXML
    private Label TIME;
    private int wpm; // Word Per Minite
    private static int idx;
    @FXML
    private Slider slider1 = new Slider();
    @FXML
    private Label Accuracy;
    private float accuracy;
    private float accuracyPerletter;

    public static void indexSetter()
    {
        Random rand = new Random();
        idx= rand.nextInt(2);
    }
    @FXML
    public void goBackHome(ActionEvent event) throws IOException {
        Stage stage = (Stage)((Node) event.getSource()).getScene().getWindow();
        stage.setScene(MainHomePage.homeScene);
    }


    @FXML
    public void initialize() {                 // The initialize() method in a JavaFX controller is called only once, when:
        // the FXML file is first loaded via FXMLLoader.load().
        // Initialize original paragraph
        updateTextFlow("");
        startTime = System.currentTimeMillis();
        slider1.setMin(0);
        slider1.setMax(s[idx].length());
        slider1.setValue(0); // Start from zero
        accuracyPerletter = 100.0F/s[idx].length();
        accuracy = 100.0F;
        Accuracy.setText("Accuracy : "+ String.valueOf(accuracy)+"%");

        // Timeline to update elapsed time every 1 second
        Timeline timer = new Timeline(new KeyFrame(Duration.seconds(1), e -> {
            long elapsedMillis = System.currentTimeMillis() - startTime;
            TIME.setText("TIME : " + String.valueOf(elapsedMillis / 1000)+"s"); // seconds
        }));
        timer.setCycleCount(Timeline.INDEFINITE);
        timer.play();

        //  System.out.println("Hello");
        // Live typing listener
        textField.textProperty().addListener((observable, oldValue, newValue) -> {    // lambda function gets called still after the initialize function ends
            // observable = the property being observed (textField.textProperty())  // Javafx internal string observer
            // oldValue = the previous text
            // newValue = the updated text
            if(newValue.length()>=s[idx].length()){
                textField.setEditable(false);  // Prevent further typing
                timer.stop();
                endTime = System.currentTimeMillis();
                long durationMillis = endTime - startTime; // in milliseconds
                double durationMinutes = durationMillis / 60000.0;
                int totalWords = s[idx].length() / 5;
                int wpm = (int)(totalWords / durationMinutes);
                //  System.out.println("WPM: " + wpm);
                WPM.setText("WPM : "+ String.valueOf(wpm));
                Accuracy.setText("Accuracy : "+ String.valueOf(accuracy)+"%");
                try {
                    RecordFileEditor(wpm,accuracy);
                } catch (IOException e) {
                    throw new RuntimeException(e);
                }
            }
            slider1.setValue(newValue.length());
            updateTextFlow(newValue);
        });
        Platform.runLater(() -> textField.requestFocus());
    }
    @FXML
    private void updateTextFlow(String userInput) {
        textFlow.getChildren().clear();
        int mistake=0;
        for (int i = 0; i < s[idx].length(); i++) {
            Text t = new Text(String.valueOf(s[idx].charAt(i)));  // Text t = new Text(s1.charAt(i)); -> wrong
            //  t.setStyle("-fx-font-size: 20px;");               // The reason is: Text constructor expects a String, not a char.

            if (i < userInput.length()) {
                if (userInput.charAt(i) == s[idx].charAt(i)) {
                    t.setFill(Color.WHITE);
                } else {
                    t.setFill(Color.BLACK);
                    mistake++;
                }
            } else {
                t.setFill(Color.GREEN);
            }
            t.setStyle("-fx-font-weight: bold;");
            t.setStyle("-fx-font-size: 25px;");
            textFlow.getChildren().add(t);
        }
        accuracy = 100.0F - (mistake*accuracyPerletter);
        Accuracy.setText(String.format("Accuracy : %.2f%%", accuracy));
    }

    private void RecordFileEditor(int wpm,float accuracy) throws IOException {
        File inputFile = new File("RecordFiles/Record");
        Scanner sc = new Scanner(inputFile);
        int fileWPM=0;
        float fileAccuracy=0.0F;
        while (sc.hasNextLine()) {
            String line = sc.nextLine();
            String[] words = line.split(":");
            if(words[0].equals("WPM")){
                fileWPM = Integer.parseInt(words[1]);
            }
            else if(words[0].equals("Accuracy")){
                words[1]=words[1].replace("%","");
                fileAccuracy = Float.parseFloat(words[1]);
            }
        }
        sc.close();
        System.out.println("Old WPM: " + fileWPM + ", New WPM: " + wpm);
        System.out.println("Old Accuracy: " + fileAccuracy + ", New Accuracy: " + accuracy);

        if (wpm >= fileWPM && accuracy > fileAccuracy) {
//            File dir = new File("RecordFiles");
//            if (!dir.exists()) {
//                dir.mkdir();
//            }

            FileWriter fw = new FileWriter("RecordFiles/Record", false);
            fw.write("WPM:" + wpm + "\n");
            fw.write("Accuracy:" + accuracy + "\n");
            fw.close();

            System.out.println("Record updated.");
        } else {
            System.out.println("Not a better record, so file not updated.");
        }
    }
}
