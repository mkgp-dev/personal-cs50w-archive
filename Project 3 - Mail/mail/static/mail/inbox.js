document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  // By default, load the inbox
  load_mailbox('inbox');

  // Send email
  document.querySelector('#compose-form').onsubmit = function (e) {
    e.preventDefault();

    const recipients = document.querySelector('#compose-recipients').value;
    const subject = document.querySelector('#compose-subject').value;
    const body = document.querySelector('#compose-body').value;

    call_data_api('/emails', { recipients, subject, body })
      .then(result => {
        if (result.message) {
          load_mailbox('sent');
        } else if (result.error) {
          message_log(result.error, 'danger');
        }
      })
      // Should catch an unknown error
      .catch(error => {
        message_log('An error has occured.', 'danger');
        console.log(error);
      });
  };
});

function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#compose-view').className = 'normal-fade-in';

  // Clear out composition fields
  document.querySelector('#compose-header').innerHTML = 'New Email';
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  // Reset current_id
  current_id = null;

  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Fetch request
  // Added timeout to call API properly
  setTimeout(() => {
    call_api(`/emails/${mailbox}`)
      .then(result => {
        const container = document.querySelector('#emails-view');

        if (result && result != 0) {
          const div_container = document.createElement('div');
          div_container.className = 'list-group normal-fade-in';

          result.forEach(email => {
            const list_container = document.createElement('div');
            list_container.className = `email-id-${email.id} list-group-item list-group-item-action flex-column align-items-start`;
            list_container.innerHTML = `
              <div class="d-flex w-100 justify-content-between">
                <h5 class="mb-1">${email.subject}</h5>
                <small class="text-muted">${email.timestamp}</small>
              </div>
              <p class="mb-1">${email.sender}</p>
              <button class="btn btn-outline-primary btn-sm float-end d-none" id="unarchive">Unarchive</button>
            `;

            // For inbox
            if (mailbox == 'inbox') {
              if (!email.read) {
                list_container.classList.add('list-group-item-info');
              }

              // View email
              list_container.addEventListener('click', () => {
                view_email(email.id);
              });
            } else if (mailbox == 'sent') {
              list_container.classList.remove('list-group-item-action');
            } else if (mailbox == 'archive') {
              list_container.classList.remove('list-group-item-action');
              button = list_container.querySelector('#unarchive');

              button.classList.remove('d-none');
              button.addEventListener('click', () => {
                const bool = bool_put(`/emails/${email.id}`, 'archived', false);

                if (bool) {
                  load_mailbox('inbox');
                  message_log('You have successfully unarchived an email.', 'success');
                } else {
                  message_log('Failed to proceed your request.', 'danger');
                }
              });
            }
            
            div_container.append(list_container);
          });

          container.append(div_container);
        } else {
          const none_container = document.createElement('p');
          none_container.className = 'm-0 normal-fade-in';
          none_container.innerHTML = 'Nothing to see here.';

          container.append(none_container);
        }
      })
      // Should catch an unknown error
      .catch(error => {
        message_log('An error has occured.', 'danger');
        console.log(error);
      });
  }, 100);
}

// JavaScript
// https://developer.mozilla.org/en-US/docs/Web/API/Element

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

function bool_put(request, string, bool) {
  return fetch(request, {
    method: 'PUT',
    body: JSON.stringify({ [string]: bool })
  })
  .then(response => {
    if (response.status === 200 || response.status === 204) {
      return true;
    } else {
      return false;
    }
  })
  .catch(error => {
    return false;
  });
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

// View email
let current_id = null;
function view_email(id) {
  if (current_id !== null && current_id !== id) {
    reset_view_email(current_id);
  }

  const email_container = document.querySelector(`.email-id-${id}`);

  if (!email_container) {
    return;
  }

  if (current_id === id) {
    reset_view_email(current_id);
    return;
  }

  email_container.classList.add('normal-fade-out');


  call_api(`/emails/${id}`)
    .then(result => {
      email_container.classList.remove('list-group-item-info');
      email_container.classList.remove('list-group-item-action');
      email_container.classList.remove('normal-fade-out');
      email_container.innerHTML = `
        <div class="normal-fade-in">
          <div class="d-flex w-100 justify-content-between">
            <h5 class="mb-1"><span class="badge text-bg-primary">${result.sender}</span> ${result.subject}</h5>
            <small class="text-muted">${result.timestamp}</small>
          </div>
          <div class="card mt-2 mb-2">
            <div class="card-header d-flex justify-content-between align-items-center">
              <div class="d-flex align-items-center">
                <p class="m-0">Sent for <span class="text-decoration-underline">${result.recipients.join(', ')}</span></p>
              </div>
              <button class="btn btn-outline-primary btn-sm" id="archive">Archive</button>
            </div>
            <div class="card-body">
              <p class="mb-0">${result.body.replace(/\n/g, '<br>')}</p>
            </div>
          </div>
          <button type="button" class="btn btn-sm btn-primary" id="reply">Reply</button>
        </div>
      `;

      // Trigger read
      if (!result.read) {
        bool_put(`/emails/${id}`, 'read', true)
      }

      // Trigger archive
      document.querySelector('#archive').addEventListener('click', () => {
        bool = bool_put(`/emails/${id}`, 'archived', true)

        if (bool) {
          load_mailbox('inbox');
          message_log('You have successfully archived an email.', 'success');
        } else {
          message_log('Failed to proceed your request.', 'danger');
        }
      });

      // Trigger reply
      document.querySelector('#reply').addEventListener('click', () => {
        reply_email(result);
      });

      current_id = id;
    })
    .catch(error => {
      message_log('An error has occured.', 'danger');
      console.log(error);
    });
}

// Reset email view for aesthetics
function reset_view_email(id) {
  const email_container = document.querySelector(`.email-id-${id}`);

  call_api('/emails/inbox')
    .then(result => {
      const email = result.find(e => e.id === id);
      email_container.innerHTML = `
        <div class="d-flex w-100 justify-content-between">
          <h5 class="mb-1">${email.subject}</h5>
          <small class="text-muted">${email.timestamp}</small>
        </div>
        <p class="mb-1">${email.sender}</p>
      `;

      email_container.classList.add('list-group-item-action');
      email_container.classList.remove('normal-fade-in');
    })
    .catch(error => {
      message_log('An error has occured.', 'danger');
      console.log(error);
    });

  if (current_id === id) {
    current_id = null;
  }
}

// Reply email
function reply_email(data) {
  // Hide page
  document.querySelector('#emails-view').style.display = 'none';

  // Re'using this, showing fade animation
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#compose-view').className = 'normal-fade-in';

  document.querySelector('#compose-header').innerHTML = `Reply to ${data.sender}`;
  document.querySelector('#compose-recipients').value = data.sender;

  // Pre-fill the subject line. If "Re:" exist, ignore
  if (data.subject.startsWith('Re:')) {
    document.querySelector('#compose-subject').value = data.subject;
  } else {
    document.querySelector('#compose-subject').value = `Re: ${data.subject}`;
  }

  // Pre-fill the body of the email
  document.querySelector('#compose-body').value = `On ${data.timestamp}, ${data.sender} wrote:\n${data.body}\n\n`;
}