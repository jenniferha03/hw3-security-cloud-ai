package antra.homework31.service.impl;

import antra.homework31.movie.MovieData;
import antra.homework31.movie.MovieResponse;
import antra.homework31.service.MovieService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.util.UriComponentsBuilder;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;

@Service
public class MovieServiceImpl implements MovieService {

    @Autowired
    private RestTemplate restTemplate;

    private final String BASE_URL = "https://jsonmock.hackerrank.com/api/moviesdata/search/";

    @Override
    public List<MovieData> getAllMovies() {

        MovieResponse firstPage = searchMovies(null, null, 1);
        int totalPages = firstPage.getTotalPages();

        List<CompletableFuture<MovieResponse>> futures = new ArrayList<>();

        for (int i = 1; i <= totalPages; i++) {

            int currentPage = i;
            CompletableFuture<MovieResponse> future = CompletableFuture.supplyAsync(() ->
                    searchMovies(null, null, currentPage)
            );
            futures.add(future);
        }

        CompletableFuture.allOf(futures.toArray(new CompletableFuture[0])).join();

        List<MovieData> allMovies = new ArrayList<>();

        for (CompletableFuture<MovieResponse> f : futures) {
            allMovies.addAll(f.join().getData());
        }

        return allMovies;
    }

    @Override
    public MovieResponse searchMovies(String title, Integer year, Integer page) {

        String url = UriComponentsBuilder.fromUriString(BASE_URL)
                .queryParam("Title", title)
                .queryParam("Year", year)
                .queryParam("page", page)
                .build()
                .toUriString();

        return restTemplate.getForObject(url, MovieResponse.class);
    }
}
