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
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.List;
import java.util.Objects;
import javafx.scene.control.Button;
import javafx.util.Duration;

import javax.swing.*;
import java.util.Random;
import java.util.Scanner;

public class SoloController {
    @FXML
    private Label WPM;
    private String[] s=
    {
        "Quantum mechanics is the branch of physics that deals with the behavior of particles at the atomic and subatomic scale. It introduces concepts such as wave-particle duality, superposition, and entanglement, which defy classical intuition. Unlike classical mechanics, quantum theory suggests that the act of observation affects the system being observed.",
            "Lionel Messi, the little boy from Rosario, stands atop the world finally, eternally. He has danced through the ages, a symphony of left-footed genius, and now, at last, the golden trophy is his. The World Cup, long elusive, rests in the hands of the man who made the beautiful game more beautiful. Argentina weeps, the world applauds, and football glorious, magical football bows at the feet of its humble king.",
           "Napoleon Bonaparte was a brilliant French general who became emperor in 1804. He led many successful battles across Europe and introduced reforms that shaped modern laws. Despite his victories, he was eventually defeated and exiled to the island of Saint Helena."
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
      // idx= rand.nextInt(3);
        idx=2;
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
                wpmRecordEditor(wpm);
                accuracyRecordEditor(accuracy);
            } catch (IOException e) {
                throw new RuntimeException(e);
            }
        }
        slider1.setValue(newValue.length());
        updateTextFlow(newValue);
    });
    // Set focus to the text field when scene is ready
    Platform.runLater(() -> textField.requestFocus()); // didn't need to place the cursor for starting type
}
    @FXML
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
            // Calculate accuracy based on current correct letters
//            accuracy = 100.0F - (mistake*accuracyPerletter);
//            Accuracy.setText(String.format("Accuracy : %.2f%%", accuracy));

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

    private void wpmRecordEditor(int wpm) throws IOException {
        // Path to your file
        Path filePath = Paths.get("RecordFiles/wpmRecord");

        // Step 1: Read all lines
        List<String> lines = Files.readAllLines(filePath);

        // Step 2: Remove the first line if there are at least one line
        if (!lines.isEmpty()) {
            lines.remove(0);
        }

        // Step 3: Add new line at the end
        lines.add(String.valueOf(wpm));

        // Step 4: Write updated lines back to file
        Files.write(filePath, lines);

        System.out.println("First line deleted and new line appended.");
    }
    private void accuracyRecordEditor(float accuracy) throws IOException {
        // Path to your file
        Path filePath = Paths.get("RecordFiles/accuracyRecord");

        // Step 1: Read all lines
        List<String> lines = Files.readAllLines(filePath);

        // Step 2: Remove the first line if there are at least one line
        if (!lines.isEmpty()) {
            lines.remove(0);
        }

        // Step 3: Add new line at the end
        lines.add(String.valueOf(accuracy));

        // Step 4: Write updated lines back to file
        Files.write(filePath, lines);

        System.out.println("First line deleted and new line appended.");
    }
}
