package antra.homework31.controller;

import java.util.List;

import antra.homework31.movie.MovieData;
import antra.homework31.movie.MovieResponse;
import antra.homework31.service.MovieService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/v1/movies")
@PreAuthorize("hasRole('USER')")
public class MovieController {

    @Autowired
    private MovieService movieService;

    @GetMapping
    public List<MovieData> getAllMovies() {
        return movieService.getAllMovies();
    }

    @GetMapping(params = "Title")
    public MovieResponse searchMovies(
            @RequestParam(value = "Title") String title,
            @RequestParam(value = "Year", required = false) Integer year,
            @RequestParam(value = "page", required = false, defaultValue = "1") Integer page
    ) {
        return movieService.searchMovies(title, year, page);
    }
}
