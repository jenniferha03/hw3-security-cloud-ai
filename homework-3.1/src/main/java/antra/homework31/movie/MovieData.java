package antra.homework31.movie;

import com.fasterxml.jackson.annotation.JsonProperty;

public class MovieData {

    @JsonProperty("Title")
    private String title;

    @JsonProperty("Year")
    private int year;

    @JsonProperty("imdbID")
    private String imdbID;

    public MovieData() {}

    public MovieData(String title, int year, String imdbID) {
        this.title = title;
        this.year = year;
        this.imdbID = imdbID;
    }

    public String getTitle() {
        return title;
    }

    public void setTitle(String title) {
        this.title = title;
    }

    public int getYear() {
        return year;
    }

    public void setYear(int year) {
        this.year = year;
    }

    public String getImdbID() {
        return imdbID;
    }

    public void setImdbID(String imdbID) {
        this.imdbID = imdbID;
    }
}
