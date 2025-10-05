module.exports = {
  apps: [
    {
      name: 'kvtm-backend',
      cwd: './backend/src',
      script: 'poetry',
      args: 'run gunicorn -b 0.0.0.0:3001 --timeout 120 --access-logfile - --error-logfile - main:app',
      interpreter: 'none',
      env: {
        NODE_ENV: 'production',
        FLASK_ENV: 'production'
      },
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      error_file: '../../logs/backend-error.log',
      out_file: '../../logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      instances: 1,
      exec_mode: 'fork'
    },
    {
      name: 'kvtm-frontend',
      cwd: './frontend',
      script: 'npx',
      args: 'serve -s dist -p 3000',
      interpreter: 'none',
      env: {
        NODE_ENV: 'production'
      },
      autorestart: true,
      watch: false,
      max_memory_restart: '500M',
      error_file: '../logs/frontend-error.log',
      out_file: '../logs/frontend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      instances: 1,
      exec_mode: 'fork'
    }
  ]
}
