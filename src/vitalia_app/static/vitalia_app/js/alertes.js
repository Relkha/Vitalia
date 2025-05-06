// Gestion des alertes
function initAlertManagement() {
  // Gestion des filtres
  const filterSelects = document.querySelectorAll('.alert-filters select');
  const clearFiltersBtn = document.querySelector('.btn-clear-filters');
  const alertCards = document.querySelectorAll('.alert-card');

  // Appliquer les filtres
  filterSelects.forEach(select => {
    select.addEventListener('change', applyFilters);
  });

  // Réinitialiser les filtres
  clearFiltersBtn.addEventListener('click', () => {
    filterSelects.forEach(select => {
      select.value = 'all';
    });
    applyFilters();
  });

  function applyFilters() {
    const severityFilter = document.getElementById('filter-severity').value;
    const typeFilter = document.getElementById('filter-type').value;
    const statusFilter = document.getElementById('filter-status').value;
    const dateFilter = document.getElementById('filter-date').value;

    alertCards.forEach(card => {
      let showCard = true;

      // Vérifier le niveau de priorité
      if (severityFilter !== 'all' && !card.classList.contains(`priority-${severityFilter}`)) {
        showCard = false;
      }

      // Vérifier le type d'alerte
      if (typeFilter !== 'all' && card.dataset.type !== typeFilter) {
        showCard = false;
      }

      // Vérifier le statut
      if (statusFilter !== 'all' && card.dataset.status !== statusFilter) {
        showCard = false;
      }

      // Vérifier la date - cela nécessiterait plus de logique
      // avec les dates réelles des alertes

      // Afficher ou masquer la carte
      card.style.display = showCard ? 'block' : 'none';
    });
  }

  // Gestion des actions sur les alertes
  const acknowledgeButtons = document.querySelectorAll('.alert-acknowledge');
  const resolveButtons = document.querySelectorAll('.btn-resolve');
  const detailButtons = document.querySelectorAll('.btn-details');

  acknowledgeButtons.forEach(button => {
    button.addEventListener('click', function() {
      const alertId = this.dataset.id;
      acknowledgeAlert(alertId);
    });
  });

  resolveButtons.forEach(button => {
    button.addEventListener('click', function() {
      const alertId = this.dataset.id;
      resolveAlert(alertId);
    });
  });

  detailButtons.forEach(button => {
    button.addEventListener('click', function() {
      const alertId = this.dataset.id;
      showAlertDetails(alertId);
    });
  });

  // Gestion du modal
  const modal = document.getElementById('alert-detail-modal');
  const closeBtn = modal.querySelector('.close');
  const modalClose = document.getElementById('modal-close');
  const modalAcknowledge = document.getElementById('modal-acknowledge');
  const modalResolve = document.getElementById('modal-resolve');

  closeBtn.addEventListener('click', closeModal);
  modalClose.addEventListener('click', closeModal);

  modalAcknowledge.addEventListener('click', function() {
    const alertId = this.dataset.id;
    acknowledgeAlert(alertId);
    closeModal();
  });

  modalResolve.addEventListener('click', function() {
    const alertId = this.dataset.id;
    resolveAlert(alertId);
    closeModal();
  });

  function closeModal() {
    modal.style.display = 'none';
  }

  // Fermer le modal quand on clique en dehors
  window.addEventListener('click', function(event) {
    if (event.target === modal) {
      closeModal();
    }
  });

  // Fonctions d'action sur les alertes
  function acknowledgeAlert(alertId) {
    fetch(`/api/alertes/${alertId}/acknowledge/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Mettre à jour l'interface
        const card = document.querySelector(`.alert-card[data-id="${alertId}"]`);
        card.dataset.status = 'in-progress';

        // Notification de succès
        showNotification('Alerte prise en charge avec succès');
      }
    })
    .catch(error => {
      console.error('Erreur:', error);
    });
  }

  function resolveAlert(alertId) {
    fetch(`/api/alertes/${alertId}/resolve/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      }
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        // Mettre à jour l'interface
        const card = document.querySelector(`.alert-card[data-id="${alertId}"]`);
        card.dataset.status = 'resolved';

        // Notification de succès
        showNotification('Alerte marquée comme résolue');
      }
    })
    .catch(error => {
      console.error('Erreur:', error);
    });
  }

  function showAlertDetails(alertId) {
    fetch(`/api/alertes/${alertId}/details/`)
    .then(response => response.json())
    .then(data => {
      const detailContent = document.getElementById('alert-detail-content');

      // Générer le contenu HTML pour les détails
      let html = `
        <div class="alert-detail-header priority-${data.priority}">
          <h3>${data.title}</h3>
          <div class="alert-detail-meta">
            <p><strong>Date et heure :</strong> ${formatDate(data.created_at)}</p>
            <p><strong>Priorité :</strong> ${data.priority_display}</p>
            <p><strong>Type :</strong> ${data.type_display}</p>
            <p><strong>Statut :</strong> ${data.status_display}</p>
          </div>
        </div>
        <div class="alert-detail-body">
          <p>${data.description}</p>
      `;

      if (data.device) {
        html += `
          <div class="detail-section">
            <h4>Informations sur l'appareil</h4>
            <p><strong>Nom :</strong> ${data.device.name}</p>
            <p><strong>Type :</strong> ${data.device.type}</p>
            <p><strong>Emplacement :</strong> ${data.device.location}</p>
          </div>
        `;
      }

      if (data.resident) {
        html += `
          <div class="detail-section">
            <h4>Informations sur le résident</h4>
            <p><strong>Nom :</strong> ${data.resident.first_name} ${data.resident.last_name}</p>
            <p><strong>Chambre :</strong> ${data.resident.room_number || 'Non assignée'}</p>
          </div>
        `;
      }

      if (data.history && data.history.length > 0) {
        html += `
          <div class="detail-section">
            <h4>Historique</h4>
            <ul class="alert-history">
        `;

        data.history.forEach(entry => {
          html += `
            <li>
              <span class="history-date">${formatDate(entry.date)}</span>
              <span class="history-action">${entry.action}</span>
              <span class="history-user">${entry.user}</span>
            </li>
          `;
        });

        html += `
            </ul>
          </div>
        `;
      }

      html += `</div>`;

      // Injecter le HTML dans le modal
      detailContent.innerHTML = html;

      // Mettre à jour les données des boutons du modal
      modalAcknowledge.dataset.id = alertId;
      modalResolve.dataset.id = alertId;

      // Afficher le modal
      modal.style.display = 'block';
    })
    .catch(error => {
      console.error('Erreur:', error);
    });
  }

  // Fonctions utilitaires
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  function showNotification(message) {
    // Créer une notification HTML
    const notification = document.createElement('div');
    notification.className = 'toast-notification';
    notification.textContent = message;

    // Ajouter au document
    document.body.appendChild(notification);

    // Afficher avec animation
    setTimeout(() => {
      notification.classList.add('show');
    }, 10);

    // Supprimer après 3 secondes
    setTimeout(() => {
      notification.classList.remove('show');
      setTimeout(() => {
        notification.remove();
      }, 300);
    }, 3000);
  }
}