document.addEventListener('DOMContentLoaded', function() {
	// Load post
	load_post(current_page);

	// Create post
	const create_post = document.querySelector('#post-form');
	if (create_post) {
		create_post.addEventListener('submit', async function(e) {
			e.preventDefault();

			const content = document.querySelector('#post-content').value;

			call_data_api('/posts/create', { content })
				.then(result => {
					if (result.message) {
						load_post(current_page);
						message_log(result.message, 'success');
						bootstrap.Modal.getInstance(document.querySelector('#create-post')).hide();

						// Reset
						document.querySelector('#post-content').value = '';
					} else if (result.error) {
						message_log(result.error, 'danger');
					}
				})
				.catch(error =>{
					message_log('An error has occured.', 'danger');
					console.error(error);
				});
		});
	}
});

// Universal fetch
function call_data_api(request, data) {
  return fetch(request, {
    method: 'POST',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => response.json());
}

function call_api(request) {
  return fetch(request, {
    method: 'GET',
  }).then(response => response.json());
}

function call_put_api(request, data) {
  return fetch(request, {
    method: 'PUT',
    body: JSON.stringify(data),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => response.json());
}

// Message log
function message_log(message, type = 'success') {
  const container = document.querySelector('#message-container');
  const id = `log-${Date.now()}`;

  const template = `
    <div id="${id}" class="alert alert-${type} alert-dismissible fade show message-slide" role="alert">
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
      <p class="mb-0">${message}</p>
    </div>
  `;

  container.insertAdjacentHTML('beforeend', template);

  setTimeout(() => {
    const alertbox = document.querySelector(`#${id}`);
    if (alertbox) {
      alertbox.classList.add('message-fade');
      alertbox.addEventListener('animationend', () => alertbox.remove());
    }
  }, 5000);
}

// Load index
// Note to myself:
// This should be applicable to all post
// OK! Modify views.py to synchronize All Post, Profile, Following with this function
// OK! Avoid JavaScript errors in Console
async function load_post(page) {
	const request_url = document.getElementById('query-url');
	const request_page = document.getElementById('query-page');
	const request_user = document.getElementById('query-username');

	if (!request_url && !request_page && !request_user) {
		return;
	}

	const q_url = request_url.value;
	const q_page = request_page.value;
	const q_user = request_user.value;

	setTimeout(() => {
		call_api(`${q_url}?page=${current_page}`)
			.then(result => {
				const list_container = document.querySelector('#post-list');
				list_container.classList.add('normal-fade-in');
				list_container.innerHTML = '';

				if (result.posts && result.posts != 0) {
					result.posts.forEach(post => {
						const post_container = document.createElement('li');
						post_container.className = 'list-group-item';

						if (q_page === 'profile') {
							post_container.innerHTML = `
								<div id="id-${post.id}" class="d-flex justify-content-between align-items-center">
									<p class="small text-muted m-0 mb-2">${post.username === q_user ? '<span class="span-cursor text-info edit-post me-2" data-id="' + post.id + '"><i class="fa-solid fa-pen-to-square me-1"></i>Edit</span>' : ''}This user posted at ${post.date}</p>
									${result.user_auth_bool ? `<span class="badge bg-primary rounded-pill"><i class="fa-solid fa-heart me-1"></i>${post.likes}</span>` : ''}
								</div>
								<p id="post-content-${post.id}" class="m-0">${post.content}</p>
							`;
						} else {
							post_container.innerHTML = `
								<div id="id-${post.id}" class="d-flex justify-content-between align-items-center">
									<h4 class="m-0"><a class="text-decoration-none" href="/profile/${post.username}">${post.username}</a></h4>
									${result.user_auth_bool ? `<span class="badge bg-primary rounded-pill"><i class="fa-solid fa-heart me-1 span-cursor like-post ${post.liked ? 'span-liked' : ''}" data-id="${post.id}"></i>${post.likes}</span>` : ''}
								</div>
								<p class="small text-muted m-0 mb-2">${post.username === q_user ? '<span class="span-cursor text-info edit-post me-2" data-id="' + post.id + '"><i class="fa-solid fa-pen-to-square me-1"></i>Edit</span>' : ''}${post.date}</p>
								<p id="post-content-${post.id}" class="m-0">${post.content}</p>
							`;
						}

						list_container.append(post_container);
					});

					// Edit function
					document.querySelectorAll('.edit-post').forEach(edit => {
						edit.addEventListener('click', function () {
							const id = this.getAttribute('data-id');
							const post = document.querySelector(`#post-content-${id}`);
							const content = post.innerHTML;

							// Note: The content of their post should be replaced with a textarea
							const edit_container = document.createElement('div');
							edit_container.className = 'edit-container normal-fade-in';

							const textarea_container = document.createElement('textarea');
							textarea_container.className = 'form-control mb-2';
							textarea_container.value = content;

							edit_container.append(textarea_container);
							post.replaceWith(edit_container);


							// Hide Edit
							this.style.display = 'none';

							// Create group button
							const button_container = document.createElement('div');
							button_container.className = 'd-grid gap-2 d-md-block';

							// Save button
							const save = document.createElement('button');
							save.className = 'btn btn-primary btn-sm me-2';
							save.innerHTML = 'Save';

							const cancel = document.createElement('button');
							cancel.className = 'btn btn-secondary btn-sm';
							cancel.innerHTML = 'Cancel';

							button_container.append(save);
							button_container.append(cancel);
							edit_container.append(button_container);

							// Save function
							save.addEventListener('click', () => {
								const content = textarea_container.value;

								call_put_api(`/posts/${id}/edit`, { content })
									.then(result => {
										if (result.message) {
											const revert = document.createElement('p');
											revert.id = `post-content-${id}`;
											revert.className = 'm-0';
											revert.innerHTML = result.content;

											edit_container.replaceWith(revert);
											this.style.display = '';

											message_log(result.message, 'success');
										} else if (result.error) {
											message_log(result.error, 'danger');
										}
									})
									.catch(error =>{
										message_log('An error has occured.', 'danger');
										console.error(error);
									});
							});

							// Cancel function
							cancel.addEventListener('click', () => {
								const revert = document.createElement('p');
								revert.id = `post-content-${id}`;
								revert.className = 'm-0';
								revert.innerHTML = content;

								edit_container.replaceWith(revert);
								this.style.display = '';
							});
						});
					})

					// Like function
					document.querySelectorAll('.like-post').forEach(like => {
						like.addEventListener('click', function () {
							const id = this.getAttribute('data-id');

							call_put_api(`/posts/${id}/like`, { like: !this.classList.contains('span-liked') })
								.then(result => {
									if (result.message) {
										if (result.bool) {
											this.classList.add('span-liked');
										} else {
											this.classList.remove('span-liked');
										}
										
										const like_container = this.closest('.badge');
										like_container.querySelector('i').className = `fa-solid fa-heart me-1 span-cursor like-post ${result.bool ? 'span-liked' : ''}`;
										like_container.lastChild.textContent = result.likes;
									} else if (result.error) {
										message_log(result.error, 'danger');
									}
								})
								.catch(error =>{
									message_log('An error has occured.', 'danger');
									console.error(error);
								});
						});
					});

					pagination(result);
				} else {
					const none_container = document.createElement('p');
					none_container.className = 'm-0';
					none_container.innerHTML = 'Nothing to see here.';

					list_container.append(none_container);
				}
			})
			.catch(error => {
				message_log('An error has occured.', 'danger');
				console.error(error);
			});
	}, 100);
}

// Pagination
let current_page = 1;
function pagination(data) {
	// Remove class fade of Post
	setTimeout(() => {
		const list_container = document.querySelector('#post-list');
		list_container.classList.remove('normal-fade-in');
	}, 100);

	const pagination = document.querySelector('.pagination');
	pagination.innerHTML = '';

	if (data.total === 0 || data.total === 1) {
		return;
	}

	// Previous
	const previous_li = document.createElement('li');
	previous_li.className = 'page-item' + (data.previous ? '' : ' disabled');
	previous_li.innerHTML = `<a class="page-link" href="#"><i class="fa-solid fa-angles-left"></i></a>`;
	previous_li.addEventListener('click', () => {
		if (current_page > 1) {
			current_page--;
			load_post(current_page);
		}
	});
	pagination.appendChild(previous_li);

	// Pages
	for (let i = 1; i <= data.total; i++) {
		const page_li = document.createElement('li');
		page_li.className = 'page-item' + (i === data.page ? ' active' : '');
		page_li.innerHTML = `<a class="page-link" href="#">${i}</a>`;
		page_li.addEventListener('click', () => {
			current_page = i;
			load_post(current_page);
		});
		pagination.appendChild(page_li);
	}

	// Next
	const next_li = document.createElement('li');
	next_li.className = 'page-item' + (data.next ? '' : ' disabled');
	next_li.innerHTML = `<a class="page-link" href="#"><i class="fa-solid fa-angles-right"></i></a>`;
	next_li.addEventListener('click', () => {
		if (current_page < data.total) {
			current_page++;
			load_post(current_page);
		}
	});
	pagination.appendChild(next_li);
}