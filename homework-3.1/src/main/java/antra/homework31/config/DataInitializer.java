package antra.homework31.config;

import antra.homework31.user.AppUser;
import antra.homework31.user.AppUserRepository;
import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.security.crypto.password.PasswordEncoder;

@Configuration
public class DataInitializer {

	@Bean
	CommandLineRunner seedUsers(AppUserRepository repository, PasswordEncoder passwordEncoder) {
		return args -> {
			if (repository.count() > 0) {
				return;
			}
			AppUser user = new AppUser();
			user.setUsername("user");
			user.setPassword(passwordEncoder.encode("password"));
			user.setRole("USER");
			repository.save(user);
		};
	}
}
