package com.example.typetutor;

import javafx.event.ActionEvent;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.Node;
import javafx.scene.Parent;
import javafx.scene.chart.LineChart;
import javafx.scene.control.Label;
import javafx.stage.Stage;
import java.util.*;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.nio.file.*;
import java.util.Scanner;
import javafx.scene.chart.NumberAxis;
import javafx.scene.chart.XYChart;

public class RecordContoller {
    @FXML
    private Label HIGHEST_SCORE;
    @FXML
    private Label WPM;
    @FXML
    private Label ACCURACY;
    @FXML
    private LineChart<String, Number> wpmChart;
    @FXML
    private LineChart<String, Number> accuracyChart;

    @FXML
    private void initialize() throws IOException {
        HIGHEST_SCORE.setUnderline(true);
        File inputfile = new File("RecordFiles/Record");
        Scanner sc = new Scanner(inputfile);
        while (sc.hasNextLine()) {
            String line = sc.nextLine();
            String[] fields = line.split(":");
            if(fields[0].equals("WPM")){
                WPM.setText("WPM : "+ fields[1]);
            }
            else if(fields[0].equals("Accuracy")){
            ACCURACY.setText("ACCURACY : "+ fields[1]);
            }
        }
        try {
            wpmGraph();
            accuracyGraph();
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

  //  @FXML
    void wpmGraph() throws IOException {
        // Path to your file
        Path filePath = Paths.get("RecordFiles/wpmRecord");

        // Step 1: Read all lines
        List<String> lines = Files.readAllLines(filePath);

        System.out.println("First line deleted and new line appended.");

//        stage.setTitle("Line Chart Example");

        // Define X and Y axes
        NumberAxis xAxis = new NumberAxis();
        NumberAxis yAxis = new NumberAxis();
        xAxis.setLabel("X Axis");
        yAxis.setLabel("Y Axis");

        // Create LineChart
        LineChart<Number, Number> lineChart = new LineChart<>(xAxis, yAxis);
        lineChart.setTitle("Sample Data");

        // Create a Series
        XYChart.Series<String, Number> series = new XYChart.Series<>();
        series.setName("WPM GRAPH");

        // Add data points
        for (int i = 0; i < lines.size(); i++) {
            try {
                int y = Integer.parseInt(lines.get(i).trim());
                series.getData().add(new XYChart.Data<>(String.valueOf(i + 1), y));
                System.out.println(y);
            } catch (NumberFormatException e) {
                System.out.println("Invalid number at line " + (i + 1) + ": " + lines.get(i));
            }
        }
        // Add series to chart
        wpmChart.getData().add(series);
    }

    @FXML
    private void accuracyGraph() throws IOException {
        Path filePath = Paths.get("RecordFiles/accuracyRecord");
        List<String> lines = Files.readAllLines(filePath);
        // Define X and Y axes
        NumberAxis xAxis = new NumberAxis();
        NumberAxis yAxis = new NumberAxis();
        xAxis.setLabel("X Axis");
        yAxis.setLabel("Y Axis");

        // Create LineChart
        LineChart<Number, Number> lineChart = new LineChart<>(xAxis, yAxis);
        lineChart.setTitle("Sample Data");

        // Create a Series
        XYChart.Series<String, Number> series = new XYChart.Series<>();
        series.setName("ACCURACY GRAPH");

        // Add data points
        for (int i = 0; i < lines.size(); i++) {
            try {
                float y = Float.parseFloat(lines.get(i).trim());
                series.getData().add(new XYChart.Data<>(String.valueOf(i + 1), y));
                System.out.println(y);
            } catch (NumberFormatException e) {
                System.out.println("Invalid number at line " + (i + 1) + ": " + lines.get(i));
            }
        }
        // Add series to chart
        accuracyChart.getData().add(series);
    }

    @FXML
    private void goToHomeScene(ActionEvent event) throws IOException {
        Stage stage = (Stage)((Node) event.getSource()).getScene().getWindow();
        stage.setScene(MainHomePage.homeScene);
    }
}
