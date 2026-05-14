package antra.homework31.movie;

import com.fasterxml.jackson.annotation.JsonProperty;
import java.util.List;

public class MovieResponse {

    private int page;

    @JsonProperty("total_pages")
    private int totalPages;

    private int total;

    @JsonProperty("per_page")
    private int perPage;

    private List<MovieData> data;

    public MovieResponse() {}

    public int getPage() {
        return page;
    }

    public void setPage(int page) {
        this.page = page;
    }

    public int getTotalPages() {
        return totalPages;
    }

    public void setTotalPages(int totalPages) {
        this.totalPages = totalPages;
    }

    public List<MovieData> getData() {
        return data;
    }

    public void setData(List<MovieData> data) {
        this.data = data;
    }

    public int getPerPage() {
        return perPage;
    }

    public void setPerPage(int perPage) {
        this.perPage = perPage;
    }

    public int getTotal() {
        return total;
    }

    public void setTotal(int total) {
        this.total = total;
    }
}
